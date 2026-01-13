from __future__ import annotations
from core.state import GameState

class Renderer:
    def render(self, state: GameState):
        raise NotImplementedError