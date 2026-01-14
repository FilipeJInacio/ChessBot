from __future__ import annotations
from player.render.base import Renderer
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.state import GameState

class ConsoleRenderer(Renderer):
    def render(self, state: GameState):
        print(state.board)