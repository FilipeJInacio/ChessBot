from __future__ import annotations
from core.board import Board

class GameState:
    def __init__(self, board: Board, turn: str, castling: dict, en_passant, halfmove: int, fullmove: int):
        self.board = board
        self.turn = turn
        self.castling = castling
        self.en_passant = en_passant
        self.halfmove = halfmove
        self.fullmove = fullmove

    def copy(self):
        return GameState(
            self.board.copy(),
            self.turn,
            self.castling.copy(),
            self.en_passant,
            self.halfmove,
            self.fullmove
        )
    
def classic_game_start() -> GameState:
    board = Board()
    board.piece_at_classical_setup()
    return GameState(board, "white", {"K": True, "Q": True, "k": True, "q": True}, None, 0, 1)