import zmq
import signal
from game import ChessGame
import pygame as p
import os
import chess
import threading
import uuid
import time


class BoardRenderer:
    def __init__(self):
        super().__init__()
        self.WIDTH = self.HEIGHT = 512
        self.DIMENSION = 8
        self.SQ_SIZE = self.HEIGHT // self.DIMENSION
        self.MAX_FPS = 15  # for animations, if any
        self.IMAGES = {}

    def load_images(self):
        pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']
        for piece in pieces:
            path = os.path.join('UI', 'images', f'{piece}.png')
            self.IMAGES[piece] = p.transform.scale(p.image.load(path), (self.SQ_SIZE, self.SQ_SIZE))

    def drawBoard(self, screen: p.Surface):
        colors = [p.Color("white"), p.Color("gray")]
        font = p.font.SysFont(None, int(self.SQ_SIZE * 0.25))

        for r in range(self.DIMENSION):
            for c in range(self.DIMENSION):
                color = colors[(r + c) % 2]
                rect = p.Rect(
                    c * self.SQ_SIZE,
                    r * self.SQ_SIZE,
                    self.SQ_SIZE,
                    self.SQ_SIZE
                )
                p.draw.rect(screen, color, rect)

                # Algebraic notation
                file_char = chr(ord('a') + c)
                rank_char = str(self.DIMENSION - r)
                label = file_char + rank_char

                text_surface = font.render(label, True, p.Color("black"))
                text_rect = text_surface.get_rect()

                # Position text in lower-right corner of the square
                text_rect.bottomright = (
                    rect.right - 4,
                    rect.bottom - 2
                )
                screen.blit(text_surface, text_rect)

    def drawPieces(self, screen: p.Surface, board: chess.Board):
        for r in range(self.DIMENSION):
            for c in range(self.DIMENSION):
                piece = board.piece_at(chess.square(c, 7-r))
                color_c = 'w' if piece is not None and piece.color == chess.WHITE else 'b'
                piece_c = piece.symbol().upper() if piece is not None else None
                if piece is not None:
                    screen.blit(self.IMAGES[f'{color_c}{piece_c}'], p.Rect(c * self.SQ_SIZE, r * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE))
        
    def render(self, game: ChessGame, last_move: chess.Move):
        self.drawBoard(self.screen)
        if last_move is not None:
            # highlight last move
            s = p.Surface((self.SQ_SIZE, self.SQ_SIZE))
            s.set_alpha(100)  # transparency value
            s.fill(p.Color('yellow'))
            fr = last_move.from_square
            to = last_move.to_square
            self.screen.blit(s, (chess.square_file(fr) * self.SQ_SIZE, (7 - chess.square_rank(fr)) * self.SQ_SIZE))
            self.screen.blit(s, (chess.square_file(to) * self.SQ_SIZE, (7 - chess.square_rank(to)) * self.SQ_SIZE))

        if game.board.is_check():
            # highlight king in check
            king_pos = game.board.king(game.board.turn)
            s = p.Surface((self.SQ_SIZE, self.SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('red'))
            self.screen.blit(s, (chess.square_file(king_pos) * self.SQ_SIZE, (7 - chess.square_rank(king_pos)) * self.SQ_SIZE))
        self.drawPieces(self.screen, game.board)


class GUI_pygame:
    def __init__(self):
        self.game = ChessGame()

        self.context = zmq.Context()

        self.running = True
        self.selected_move = None

        # Threads
        self.pygame_thread = threading.Thread(target=self._pygame, daemon=True)
        self.client_thread = threading.Thread(target=self._client, daemon=True)
        self.subscriber_thread = threading.Thread(target=self._subscriber, daemon=True)
        self.state_lock = threading.Lock() # To protect shared state
        self.move_event = threading.Event()
        self.start_event = threading.Event()

        # Signal handling
        signal.signal(signal.SIGINT, self._shutdown_signal)
        signal.signal(signal.SIGTERM, self._shutdown_signal)

    def _shutdown_signal(self, sig, frame):
        print("Shutdown signal received")
        self.running = False

    def _client(self):
        game = ChessGame()

        self.dealer = self.context.socket(zmq.DEALER)
        self.dealer.setsockopt(zmq.IDENTITY, uuid.uuid4().bytes)
        self.dealer.setsockopt(zmq.RCVTIMEO, 200)
        self.dealer.setsockopt(zmq.LINGER, 0)
        self.dealer.connect("tcp://localhost:5557")

        state = "joining"

        # send join request
        self.dealer.send_multipart([b"join", b""])

        # wait for join ack
        while self.running:
            try:
                msg = self.dealer.recv_multipart()
            except zmq.Again:
                continue  

            msg_type = msg[0]
            payload = msg[1] if len(msg) > 1 else b""

            if msg_type == b"server_shutdown":
                print("Server is shutting down")
                self.running = False
                continue

            if msg_type == b"game_over":
                winner = payload.decode("utf-8") if payload else "Draw"
                print(f"Game over! Winner: {winner}")
                self.running = False
                continue

            # STATE 2
            if state == "playing":
                if msg_type == b"your_turn":
                    # what was the last move?
                    last_move_uci = payload.decode("utf-8") if payload else None

                    if last_move_uci:
                        game.make_move(last_move_uci)

                    self.move_event.wait()
                    move_uci = self.selected_move
                    self.move_event.clear()

                    game.make_move(move_uci)

                    self.dealer.send_multipart([b"move", move_uci.encode("utf-8")])

                    state = "waiting_for_move_ack"
                continue

            # STATE 3
            if state == "waiting_for_move_ack":
                if msg_type == b"move_ack":
                    state = "playing"
                elif msg_type == b"move_nack":
                    raise RuntimeError("Move was rejected by server")
                continue

            # STATE 1
            if state == "joining":
                if msg_type == b"join_ack":
                    print("Joined game")
                    self.color = payload.decode("utf-8")
                    game.reset()
                    state = "playing"
                elif msg_type == b"join_nack":
                    print("Join request denied")
                    return
                
        self.dealer.close()
        self.context.term()



    def _subscriber(self):
        self.sub = self.context.socket(zmq.SUB)
        self.sub.connect("tcp://localhost:5556")
        self.sub.setsockopt_string(zmq.SUBSCRIBE, "")
        self.sub.setsockopt(zmq.RCVTIMEO, 200)  # exit if no message in 2s

        self.start_event.wait()


        last_msg = b""
        while self.running:
            try:
                msg = self.sub.recv_json()
                if msg != last_msg:
                    with self.state_lock:
                        self.game.from_fen(msg["fen"])
                        self.render.render(self.game, chess.Move.from_uci(msg["last_move"]) if msg["last_move"] else None)
                        self.clock.tick(self.render.MAX_FPS)
                        p.display.flip()

                    last_msg = msg
                    
            except zmq.Again:
                self.running = False
                print("Timeout: No message received")

        self.sub.close()
        self.context.term()
        print("SUB client terminated")

    def _pygame(self):
        self.render = BoardRenderer()
        p.init()
        self.render.screen = p.display.set_mode((self.render.WIDTH, self.render.HEIGHT))
        p.display.set_caption('Chess')
        self.clock = p.time.Clock()
        self.render.screen.fill(p.Color("white"))
        self.render.load_images()

        dragging = False
        drag_start_sq = None
        drag_piece = None
        mouse_pos = (0, 0)


        self.start_event.set()
        while self.running:
            for e in p.event.get():
                if e.type == p.QUIT:
                    self.running = False
                elif e.type == p.MOUSEBUTTONDOWN and e.button == 1:
                    mouse_pos = p.mouse.get_pos()
                    col = mouse_pos[0] // self.render.SQ_SIZE
                    row = mouse_pos[1] // self.render.SQ_SIZE
                    square = chess.square(col, 7 - row)

                    piece = self.game.board.piece_at(square)
                    if piece:
                        dragging = True
                        drag_start_sq = square
                        drag_piece = piece

                elif e.type == p.MOUSEMOTION:
                    mouse_pos = p.mouse.get_pos()

                elif e.type == p.MOUSEBUTTONUP and e.button == 1 and dragging:
                    mouse_pos = p.mouse.get_pos()
                    col = mouse_pos[0] // self.render.SQ_SIZE
                    row = mouse_pos[1] // self.render.SQ_SIZE
                    target_sq = chess.square(col, 7 - row)

                    move = chess.Move(drag_start_sq, target_sq)

                    # Pawn promotion
                    if drag_piece.piece_type == chess.PAWN and chess.square_rank(target_sq) in (0, 7):
                        # is it even a legal move?
                        test_move = chess.Move(drag_start_sq, target_sq, promotion=chess.QUEEN)
                        if test_move not in self.game.board.legal_moves:
                            dragging = False
                            drag_start_sq = None
                            drag_piece = None
                            continue
                        promotion_choice = None
                        while promotion_choice not in ['q', 'r', 'b', 'n']:
                            promotion_choice = input("Promote to (q, r, b, n): ").lower()
                        promotion_map = {
                            'q': chess.QUEEN,
                            'r': chess.ROOK,
                            'b': chess.BISHOP,
                            'n': chess.KNIGHT
                        }
                        move = chess.Move(drag_start_sq, target_sq,
                                        promotion=promotion_map[promotion_choice])

                    with self.state_lock:
                        if move in self.game.board.legal_moves:
                            self.selected_move = move.uci()
                            self.move_event.set()

                    dragging = False
                    drag_start_sq = None
                    drag_piece = None







    def run(self):
        self.client_thread.start()
        self.pygame_thread.start()
        self.subscriber_thread.start()

        try:
            while self.running:
                time.sleep(1)
        finally:
            self.client_thread.join()
            self.pygame_thread.join()
            self.subscriber_thread.join()
            self.context.term()
            print("Terminating")







if __name__ == "__main__":
    gui = GUI_pygame()
    gui.run()