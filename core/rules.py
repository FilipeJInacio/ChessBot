from core.move import Move
from core.state import GameState

class RulesEngine:
    def legal_moves(self, state: GameState) -> list[Move]:
        ...

    def is_checkmate(self, state: GameState) -> bool:
        ...

    def apply_move(self, state: GameState, move: Move) -> GameState:
        new_state = state.copy()
        ...
        return new_state