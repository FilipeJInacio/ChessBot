from __future__ import annotations

from typing import TYPE_CHECKING

from core.pieces.pieces import Pawn, Rook, Knight, Bishop, Queen, King

if TYPE_CHECKING:
    from core.state import GameState
    from core.move import Move

class RulesEngine:
    def legal_moves(self, state: GameState) -> list[Move]:
        king_pos = state.get_piece(King(state.turn))
        
        if state.is_in_check:
            print(f"{state.turn} is in check")



        moves = []
        for row in range(8):
            for col in range(8):
                piece = state.get_piece_at((row, col))
                if piece is not None:
                    if piece.color == state.turn:
                        moves.extend(piece.possible_moves((row, col), state))
        return moves

    def is_in_check(self, state: GameState, king_pos: tuple[int, int]) -> bool:
        opponent_color = 'black' if state.turn == 'white' else 'white'
        for row in range(8):
            for col in range(8):
                piece = state.get_piece_at((row, col))
                if piece is not None and piece.color == opponent_color:
                    possible_moves = piece.possible_moves((row, col), state)
                    for move in possible_moves:
                        if move.to_sq == king_pos:
                            return True
        return False

    def apply_move(self, state: GameState, move: Move) -> GameState:
        new_state = state.copy()

        # switch turn
        new_state.turn = 'black' if state.turn == 'white' else 'white'

        # move piece
        piece = new_state.get_piece_at(move.from_sq)
        new_state.set_piece_at(move.to_sq, piece)
        new_state.set_piece_at(move.from_sq, None)

        # en passant handling
        if move.en_passant:
            new_state.en_passant = None

        # double row pawn move handling
        if isinstance(piece, Pawn):
            if abs(move.to_sq[1] - move.from_sq[1]) == 2:
                new_state.en_passant = (move.from_sq[0], (move.from_sq[1] + move.to_sq[1]) // 2)
        else:
            new_state.en_passant = None
        
        # promotion handling
        if move.promotion is not None:
            if move.promotion == 'Q' or move.promotion == 'q':
                new_state.set_piece_at(move.to_sq, Queen(piece.color))
            elif move.promotion == 'R' or move.promotion == 'r':
                new_state.set_piece_at(move.to_sq, Rook(piece.color))
            elif move.promotion == 'B' or move.promotion == 'b':
                new_state.set_piece_at(move.to_sq, Bishop(piece.color))
            elif move.promotion == 'N' or move.promotion == 'n':
                new_state.set_piece_at(move.to_sq, Knight(piece.color))

        # castling handling
        if move.castling:
            if move.to_sq[0] == 6:  # kingside
                rook_from = (7, move.from_sq[1])
                rook_to = (5, move.from_sq[1])
            else:  # queenside
                rook_from = (0, move.from_sq[1])
                rook_to = (3, move.from_sq[1])
            rook = new_state.get_piece_at(rook_from)
            new_state.set_piece_at(rook_to, rook)
            new_state.set_piece_at(rook_from, None)

        # is the adversary in check now?
        king_pos = new_state.get_piece(King(new_state.turn))
        game.is_in_check = self.is_in_check(new_state, king_pos)

        return new_state