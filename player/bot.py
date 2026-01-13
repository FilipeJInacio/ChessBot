from __future__ import annotations
from player.base import Player
from core.state import GameState
from core.move import Move
import random

class BotPlayer(Player):
    def __init__(self, renderer=None):
        self.renderer = renderer

    def render(self, state: GameState):
        if self.renderer:
            self.renderer.render(state)

    def choose_move(self, state: GameState, legal_moves: list[Move]) -> Move:
        self.render(state)
        return random.choice(legal_moves)