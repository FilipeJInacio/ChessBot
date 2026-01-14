from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.state import GameState

from core.move import Move
from core.pieces.base import Piece

class Pawn(Piece):
    def __init__(self, color: str):
        super().__init__('P' if color == 'white' else 'p', color)
        if color == 'white':
            self.possible_moves = self.possible_moves_pawn_white
        else:
            self.possible_moves = self.possible_moves_pawn_black

    def possible_moves_pawn_black(self, position: tuple[int, int], state: GameState) -> list[Move]:
        moves = []
        y, x = position
        direction = 1
        start_rank = 1
        promotion_rank = 7

       # one square forward
        if y + direction <= 7 and state.get_piece_at((y + direction, x)) is None:
            if y + direction == promotion_rank:
                for p in ['q', 'r', 'b', 'n']:
                    moves.append(Move(position, (y + direction, x), promotion=p))
            else:
                moves.append(Move(position, (y + direction, x)))

            # two squares forward from starting rank
            if y == start_rank and (state.get_piece_at((y + 2 * direction, x)) is None and state.get_piece_at((y + direction, x)) is None):
                moves.append(Move(position, (y + 2 * direction, x)))

        # captures
        for dx in (-1, 1):
            nx, ny = x + dx, y + direction
            if 0 <= nx <= 7 and 0 <= ny <= 7:
                target = state.get_piece_at((ny, nx))
                if target is not None and target.color == 'white':
                    if ny == promotion_rank:
                        for p in ['q', 'r', 'b', 'n']:
                            moves.append(Move(position, (ny, nx), promotion=p))
                    else:
                        moves.append(Move(position, (ny, nx)))

        # en passant
        if state.en_passant is not None:
            ey, ex = state.en_passant
            if ey == y + direction and abs(ex - x) == 1:
                moves.append(Move(position, (ey, ex), en_passant=True))


        return moves
    
    def possible_moves_pawn_white(self, position: tuple[int, int], state: GameState) -> list[Move]:
        moves = []
        y, x = position
        direction = -1
        start_rank = 6
        promotion_rank = 0

        # one square forward
        if y + direction >= 0 and state.get_piece_at((y + direction, x)) is None:
            if y + direction == promotion_rank:
                for p in ['Q', 'R', 'B', 'N']:
                    moves.append(Move(position, (y + direction, x), promotion=p))
            else:
                moves.append(Move(position, (y + direction, x)))

            # two squares forward from starting rank
            if y == start_rank and (state.get_piece_at((y + 2 * direction, x)) is None and state.get_piece_at((y + direction, x)) is None):
                moves.append(Move(position, (y + 2 * direction, x)))

        # captures
        for dx in (-1, 1):
            nx, ny = x + dx, y + direction
            if 0 <= nx <= 7 and 0 <= ny <= 7:
                target = state.get_piece_at((ny, nx))
                if target is not None and target.color == 'black':
                    if ny == promotion_rank:
                        for p in ['Q', 'R', 'B', 'N']:
                            moves.append(Move(position, (ny, nx), promotion=p))
                    else:
                        moves.append(Move(position, (ny, nx)))

        # en passant
        if state.en_passant is not None:
            ey, ex = state.en_passant
            if ey == y + direction and abs(ex - x) == 1:
                moves.append(Move(position, (ey, ex), en_passant=True))

        return moves
    
class Knight(Piece):
    def __init__(self, color: str):
        super().__init__('N' if color == 'white' else 'n', color)
        self.possible_moves = self.possible_moves_knight

    def possible_moves_knight(self, position: tuple[int, int], state: GameState) -> list[Move]:
        moves = []
        y, x = position
        knight_moves = [
            (2, 1), (1, 2), (-1, 2), (-2, 1),
            (-2, -1), (-1, -2), (1, -2), (2, -1)
        ]

        for dx, dy in knight_moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx <= 7 and 0 <= ny <= 7:
                target = state.get_piece_at((ny, nx))
                if target is None or target.color != self.color:
                    moves.append(Move(position, (ny, nx)))

        return moves

class Bishop(Piece):
    def __init__(self, color: str):
        super().__init__('B' if color == 'white' else 'b', color)
        self.possible_moves = self.possible_moves_bishop

    def possible_moves_bishop(self, position: tuple[int, int], state: GameState) -> list[Move]:
        moves = []
        y, x = position
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx <= 7 and 0 <= ny <= 7:
                target = state.get_piece_at((ny, nx))
                if target is None:
                    moves.append(Move(position, (ny, nx)))
                else:
                    if target.color != self.color:
                        moves.append(Move(position, (ny, nx)))
                    break
                nx += dx
                ny += dy

        return moves

class Rook(Piece):
    def __init__(self, color: str):
        super().__init__('R' if color == 'white' else 'r', color)
        self.possible_moves = self.possible_moves_rook
    
    def possible_moves_rook(self, position: tuple[int, int], state: GameState) -> list[Move]:
        moves = []
        y, x = position
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx <= 7 and 0 <= ny <= 7:
                target = state.get_piece_at((ny, nx))
                if target is None:
                    moves.append(Move(position, (ny, nx)))
                else:
                    if target.color != self.color:
                        moves.append(Move(position, (ny, nx)))
                    break
                nx += dx
                ny += dy

        return moves
    
class Queen(Piece):
    def __init__(self, color: str):
        super().__init__('Q' if color == 'white' else 'q', color)
        self.possible_moves = self.possible_moves_queen

    def possible_moves_queen(self, position: tuple[int, int], state: GameState) -> list[Move]:
        moves = []
        y, x = position
        directions = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx <= 7 and 0 <= ny <= 7:
                target = state.get_piece_at((ny, nx))
                if target is None:
                    moves.append(Move(position, (ny, nx)))
                else:
                    if target.color != self.color:
                        moves.append(Move(position, (ny, nx)))
                    break
                nx += dx
                ny += dy

        return moves

class King(Piece):
    def __init__(self, color: str):
        super().__init__('K' if color == 'white' else 'k', color)
        self.possible_moves = self.possible_moves_king

    def possible_moves_king(self, position: tuple[int, int], state: GameState) -> list[Move]:
        moves = []
        y, x = position
        king_moves = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]

        for dx, dy in king_moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx <= 7 and 0 <= ny <= 7:
                target = state.get_piece_at((ny, nx))
                if target is None or target.color != self.color:
                    moves.append(Move(position, (ny, nx)))

        # Castling king side
        if state.castling.get('K' if self.color == 'white' else 'k', False):
            if state.get_piece_at((y, 5)) is None and state.get_piece_at((y, 6)) is None:
                moves.append(Move(position, (y, 6), castling=True)) 

        # Castling queen side
        if state.castling.get('Q' if self.color == 'white' else 'q', False):
            if state.get_piece_at((y, 1)) is None and state.get_piece_at((y, 2)) is None and state.get_piece_at((y, 3)) is None:
                moves.append(Move(position, (y, 2), castling=True))

        return moves
