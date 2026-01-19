import zmq
import signal
from game import ChessGame
import pygame as p
import os
import chess
import threading
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
            self.screen.blit(s, (fr % 8 * self.SQ_SIZE, fr // 8 * self.SQ_SIZE))
            self.screen.blit(s, (to % 8 * self.SQ_SIZE, to // 8 * self.SQ_SIZE))

        if game.board.is_check():
            # highlight king in check
            king_pos = game.board.king(game.board.turn)
            s = p.Surface((self.SQ_SIZE, self.SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('red'))
            self.screen.blit(s, (king_pos % 8 * self.SQ_SIZE, king_pos // 8 * self.SQ_SIZE))
        self.drawPieces(self.screen, game.board)


class GUI_pygame:
    def __init__(self):
        self.game = ChessGame()

        self.context = zmq.Context()
        self.sub = self.context.socket(zmq.SUB)
        self.sub.connect("tcp://localhost:5556")
        self.sub.setsockopt_string(zmq.SUBSCRIBE, "")
        self.sub.setsockopt(zmq.RCVTIMEO, 200)  # exit if no message in 2s

        self.running = True

        # Threads
        self.pygame_thread = threading.Thread(target=self._pygame, daemon=True)
        self.client_thread = threading.Thread(target=self._client, daemon=True)
        self.state_lock = threading.Lock() # To protect shared state

        # Signal handling
        signal.signal(signal.SIGINT, self._shutdown_signal)
        signal.signal(signal.SIGTERM, self._shutdown_signal)


    def _shutdown_signal(self, sig, frame):
        print("Shutdown signal received")
        self.running = False

    def _client(self):
        pass


    def _pygame(self):
        pass





    def run(self):
        self.client_thread.start()
        self.pygame_thread.start()

        try:
            while self.running:
                time.sleep(1)
        finally:
            self.client_thread.join()
            self.pygame_thread.join()
            self.context.term()
            print("Terminating")









if __name__ == "__main__":
    ui = GUI_pygame()
    ui.run()