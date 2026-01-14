from __future__ import annotations
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.pieces.base import Piece


from core.pieces.pieces import Pawn, Rook, Knight, Bishop, Queen, King





class Board:
    def __init__(self):
        self.grid = np.full((8, 8), None)  # 8x8 board initialized with None

    def get_piece_at(self, position: tuple[int, int]) -> Piece:
        return self.grid[position]
    
    def set_piece_at(self, position: tuple[int, int], piece: Piece):
        self.grid[position] = piece

    def piece_at_classical_setup(self):
        self.grid[0, :] = np.array([Rook("black"), Knight("black"), Bishop("black"), Queen("black"), King("black"), Bishop("black"), Knight("black"), Rook("black")])
        self.grid[1, :] = np.array([Pawn("black"), Pawn("black"), Pawn("black"), Pawn("black"), Pawn("black"), Pawn("black"), Pawn("black"), Pawn("black")])
        self.grid[6, :] = np.array([Pawn("white"), Pawn("white"), Pawn("white"), Pawn("white"), Pawn("white"), Pawn("white"), Pawn("white"), Pawn("white")])
        self.grid[7, :] = np.array([Rook("white"), Knight("white"), Bishop("white"), Queen("white"), King("white"), Bishop("white"), Knight("white"), Rook("white")])

    def board_from_fen(self, fen: str):
        ...

    def move_piece(self, move):
        ...

    def to_dict(self):
        board_dict = {}
        for row in range(8):
            for col in range(8):
                piece = self.get_piece_at((row, col))
                if piece is not None:
                    board_dict[f"{row},{col}"] = repr(piece)
        return board_dict

    # @staticmethod
    # def from_dict(board_dict: dict):
    #     board = Board()
    #     for pos_str, piece_repr in board_dict.items():
    #         row, col = map(int, pos_str.split(","))
    #         piece = eval(piece_repr)  # Caution: using eval; ensure input is trusted
    #         board.set_piece_at((row, col), piece)
    #     return board
    

    def __repr__(self):
        display_grid = np.where(self.grid == None, '', self.grid)
        return str(display_grid)