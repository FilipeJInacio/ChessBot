from __future__ import annotations
from core.move import Move
from core.state import GameState

class RulesEngine:
    def legal_moves(self, state: GameState) -> list[Move]:
        moves = []
        for row in range(8):
            for col in range(8):
                piece = state.board.get_piece_at(row, col)
                if piece.color == state.turn:
                    moves.extend(piece.possible_moves((row, col), state))
        return moves

    def is_checkmate(self, state: GameState) -> bool:
        ...

    def apply_move(self, state: GameState, move: Move) -> GameState:
        new_state = state.copy()
        ...
        return new_state