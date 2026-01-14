from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.state import GameState

class Renderer:
    def render(self, state: GameState):
        raise NotImplementedError