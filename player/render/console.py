from __future__ import annotations
from core.state import GameState
from player.render.base import Renderer

class ConsoleRenderer(Renderer):
    def render(self, state: GameState):
        print(state.board)