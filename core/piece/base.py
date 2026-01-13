from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.state import GameState
    
from core.move import Move

class Piece:
    def __init__ (self, id: str):
        self.id = id

    def possible_moves(self, position, state: GameState) -> list[Move]:
        return NotImplementedError("This method should be implemented by subclasses.")