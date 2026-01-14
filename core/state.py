from __future__ import annotations

from core.board import Board
from copy import deepcopy
from typing import TYPE_CHECKING
from core.pieces.pieces import Pawn, Rook, Knight, Bishop, Queen, King

if TYPE_CHECKING:
    from core.pieces.base import Piece

class GameState:
    def __init__(self, board: Board, turn: str, castling: dict, en_passant: tuple[int, int] | None, halfmove: int, fullmove: int):
        self.board = board
        self.turn = turn
        self.castling = castling
        self.en_passant = en_passant
        self.halfmove = halfmove
        self.fullmove = fullmove

    def get_piece_at(self, position: tuple[int, int]) -> Piece:
        return self.board.get_piece_at(position) 
    
    def set_piece_at(self, position: tuple[int, int], piece: Piece):
        self.board.set_piece_at(position, piece)

    def to_dict(self):
        return {
            "board": self.board.to_dict(),
            "turn": self.turn,
            "castling": self.castling,
            "en_passant": self.en_passant,
            "halfmove": self.halfmove,
            "fullmove": self.fullmove,
        }
    
    @staticmethod
    def from_dict(state_dict: dict) -> GameState:
        board = Board()
        for pos_str, piece_repr in state_dict["board"].items():
            row, col = map(int, pos_str.split(","))
            color = piece_repr[0]
            piece_type = piece_repr[1]
            if piece_type == "P" or piece_type == "p":
                piece = Pawn(color)
            elif piece_type == "R" or piece_type == "r":
                piece = Rook(color)
            elif piece_type == "N" or piece_type == "n":
                piece = Knight(color)
            elif piece_type == "B" or piece_type == "b":
                piece = Bishop(color)
            elif piece_type == "Q" or piece_type == "q":
                piece = Queen(color)
            elif piece_type == "K" or piece_type == "k":
                piece = King(color)
            else:
                continue
            board.set_piece_at((row, col), piece)
        
        return GameState(board,state_dict["turn"],state_dict["castling"],tuple(state_dict["en_passant"]) if state_dict["en_passant"] is not None else None,state_dict["halfmove"],state_dict["fullmove"])

    def copy(self):
        return GameState(
            deepcopy(self.board),
            self.turn,
            self.castling.copy(),
            self.en_passant,
            self.halfmove,
            self.fullmove
        )
    
    def __repr__(self):
        return self.board.__repr__()
    
def classic_game_start() -> GameState:
    board = Board()
    board.piece_at_classical_setup()
    return GameState(board, "white", {"K": True, "Q": True, "k": True, "q": True}, None, 0, 1)