from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.state import GameState
    from core.move import Move

class Piece:
    def __init__ (self, id: str, color: str):
        self.id = id
        self.color = color

    def possible_moves(self, position: tuple[int, int], state: GameState) -> list[Move]:
        return NotImplementedError("This method should be implemented by subclasses.")
    
    def __repr__(self):
        return f"{self.color[0]}{self.id}"
    
    def __eq__(self, other):
        if not isinstance(other, Piece):
            return False
        return self.id == other.id and self.color == other.color