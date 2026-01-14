from __future__ import annotations
from core.pieces.pieces import King
from render.base import Renderer
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.state import GameState
    from core.board import Board
    from core.move import Move

import pygame as p
import os

class BoardRenderer(Renderer):
    def __init__(self):
        super().__init__()
        self.WIDTH = self.HEIGHT = 512
        self.DIMENSION = 8
        self.SQ_SIZE = self.HEIGHT // self.DIMENSION
        self.MAX_FPS = 15  # for animations, if any
        self.IMAGES = {}

    def load_images(self):
        pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'br', 'bn', 'bb', 'bq', 'bk']
        for piece in pieces:
            path = os.path.join('render', 'images', f'{piece}.png')
            self.IMAGES[piece] = p.transform.scale(p.image.load(path), (self.SQ_SIZE, self.SQ_SIZE))

    def drawBoard(self, screen: p.Surface):
        colors = [p.Color("white"), p.Color("gray")]
        for r in range(self.DIMENSION):
            for c in range(self.DIMENSION):
                color = colors[((r + c) % 2)]
                p.draw.rect(screen, color, p.Rect(c * self.SQ_SIZE, r * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE))  

    def drawPieces(self, screen: p.Surface, board: Board):
        for r in range(self.DIMENSION):
            for c in range(self.DIMENSION):
                piece = board.get_piece_at((r, c))
                if piece is not None:
                    screen.blit(self.IMAGES[piece.__repr__()], p.Rect(c * self.SQ_SIZE, r * self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE))
        

    def render(self, state: GameState, last_move: Move, is_in_check: bool):
        self.drawBoard(self.screen)
        if last_move is not None:
            # highlight last move
            s = p.Surface((self.SQ_SIZE, self.SQ_SIZE))
            s.set_alpha(100)  # transparency value
            s.fill(p.Color('yellow'))
            fr = last_move.from_sq
            to = last_move.to_sq
            self.screen.blit(s, (fr[1] * self.SQ_SIZE, fr[0] * self.SQ_SIZE))
            self.screen.blit(s, (to[1] * self.SQ_SIZE, to[0] * self.SQ_SIZE))

        print(f"Rendering board. is_in_check={is_in_check}")
        if is_in_check:
            # highlight king in check
            king_pos = state.get_piece(King(state.turn))
            s = p.Surface((self.SQ_SIZE, self.SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('red'))
            self.screen.blit(s, (king_pos[1] * self.SQ_SIZE, king_pos[0] * self.SQ_SIZE))

        self.drawPieces(self.screen, state.board)
        