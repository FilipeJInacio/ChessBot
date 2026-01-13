from __future__ import annotations
from core.state import GameState
from core.move import Move

class Player:
    def define_render(self, renderer):
        self.renderer = renderer

    def choose_move(self, state: GameState, legal_moves: list[Move]) -> Move:
        raise NotImplementedError