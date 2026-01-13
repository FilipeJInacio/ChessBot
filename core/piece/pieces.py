from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.state import GameState

from core.move import Move
from core.piece.base import Piece

class Pawn(Piece):
    def __init__(self, color: str):
        super().__init__('P' if color == 'white' else 'p')
        self.color = color
        if color == 'white':
            self.possible_moves = self.possible_moves_white
        else:
            self.possible_moves = self.possible_moves_black

    def possible_moves_white(self, position: tuple[int, int], state: GameState) -> list[Move]:
        moves = []
        y, x = position
        direction = 1
        start_rank = 1
        promotion_rank = 7

       # one square forward
        if y + direction <= 7 and state.board[x][y + direction] is None:
            if y + direction == promotion_rank:
                for p in ['Q', 'R', 'B', 'N']:
                    moves.append(Move(position, (x, y + direction), promotion=p))
            else:
                moves.append(Move(position, (x, y + direction)))

            # two squares forward from starting rank
            if y == start_rank and state.board[x][y + 2 * direction] is None:
                moves.append(Move(position, (x, y + 2 * direction)))

        # captures
        for dx in (-1, 1):
            nx, ny = x + dx, y + direction
            if 0 <= nx <= 7 and 0 <= ny <= 7:
                target = state.board[nx][ny]
                if target is not None and target.color == 'black':
                    if ny == promotion_rank:
                        for p in ['Q', 'R', 'B', 'N']:
                            moves.append(Move(position, (nx, ny), promotion=p))
                    else:
                        moves.append(Move(position, (nx, ny)))

        # en passant
        if state.en_passant_target is not None:
            ex, ey = state.en_passant_target
            if ey == y + direction and abs(ex - x) == 1:
                moves.append(
                    Move(position, (ex, ey), en_passant=True)
                )


        return moves
    
    def possible_moves_black(self, position: tuple[int, int], state: GameState) -> list[Move]:
        moves = []
        direction = -1

        return moves