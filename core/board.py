from __future__ import annotations
import numpy as np
from core.piece.pieces import Piece

class Board:
    def __init__(self):
        self.grid = np.full((8, 8), None)  # 8x8 board initialized with None

    def get_piece_at(self, position: tuple[int, int]) -> Piece:
        return self.grid[position]
    
    def set_piece_at(self, position: tuple[int, int], piece: Piece):
        self.grid[position] = piece

    def piece_at_classical_setup(self): # To REDO
        self.grid[0] = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
        self.grid[1] = ['p']*8
        self.grid[6] = ['P']*8
        self.grid[7] = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']

    def board_from_fen(self, fen: str):
        ...

    def move_piece(self, move):
        ...

