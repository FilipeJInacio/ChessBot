import zmq
import signal
from game import ChessGame
import pygame as p
import os
import chess

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
        for r in range(self.DIMENSION):
            for c in range(self.DIMENSION):
                color = colors[((r + c) % 2)]
                p.draw.rect(screen, color, p.Rect(c * self.SQ_SIZE, r * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE))  

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
            # invert fr and to
            fr = fr ^ 56
            to = to ^ 56
            self.screen.blit(s, (fr % 8 * self.SQ_SIZE, fr // 8 * self.SQ_SIZE))
            self.screen.blit(s, (to % 8 * self.SQ_SIZE, to // 8 * self.SQ_SIZE))

        if game.board.is_check():
            # highlight king in check
            king_pos = game.board.king(game.board.turn)
            king_pos = king_pos ^ 56
            s = p.Surface((self.SQ_SIZE, self.SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('red'))
            self.screen.blit(s, (king_pos % 8 * self.SQ_SIZE, king_pos // 8 * self.SQ_SIZE))
        self.drawPieces(self.screen, game.board)


class UI_pygame:
    def __init__(self):
        self.game = ChessGame()

        self.context = zmq.Context()
        self.sub = self.context.socket(zmq.SUB)
        self.sub.connect("tcp://localhost:5556")
        self.sub.setsockopt_string(zmq.SUBSCRIBE, "")
        self.sub.setsockopt(zmq.RCVTIMEO, 200)  # exit if no message in 2s

        self.running = True

        # Signal handling
        signal.signal(signal.SIGINT, self._shutdown_signal)
        signal.signal(signal.SIGTERM, self._shutdown_signal)

        self.render = BoardRenderer()

    def _shutdown_signal(self, sig, frame):
        print("Shutdown signal received")
        self.running = False

    def run(self):

        p.init()
        self.render.screen = p.display.set_mode((self.render.WIDTH, self.render.HEIGHT))
        p.display.set_caption('Chess')
        self.clock = p.time.Clock()
        self.render.screen.fill(p.Color("white"))
        self.render.load_images()

        last_msg = b""
        while self.running:
            for e in p.event.get():
                if e.type == p.QUIT:
                    self.running = False
            try:
                msg = self.sub.recv_json()
                if msg != last_msg:
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




if __name__ == "__main__":
    ui = UI_pygame()
    ui.run()