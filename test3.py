# Chess
# Chess.Board
    # __init__
# Chess.Move


import chess
board = chess.Board()

board = chess.Board(fen_string)
fen = board.fen()

move = chess.Move.from_uci("e2e4")

chess.square_file(move.from_square)  # 0–7
chess.square_rank(move.from_square)  # 0–7

board.legal_moves

board.generate_pseudo_legal_moves()

board.push(move)  ##!
board.pop()     

board.is_check()
board.is_checkmate()
board.is_stalemate()

board.is_insufficient_material()
board.can_claim_threefold_repetition()
board.can_claim_fifty_moves()

board.attacks(square)
board.is_attacked_by(chess.BLACK, square)

if board.is_attacked_by(chess.BLACK, board.king(chess.WHITE)):
    print("White is in check")


    

def generate_pseudo_legal_moves(self, from_mask: Bitboard = BB_ALL, to_mask: Bitboard = BB_ALL) -> Iterator[Move]:
    our_pieces = self.occupied_co[self.turn]

    # Generate piece moves.
    non_pawns = our_pieces & ~self.pawns & from_mask
    for from_square in scan_reversed(non_pawns):
        moves = self.attacks_mask(from_square) & ~our_pieces & to_mask
        for to_square in scan_reversed(moves):
            yield Move(from_square, to_square)

    # Generate castling moves.
    if from_mask & self.kings:
        yield from self.generate_castling_moves(from_mask, to_mask)

    # The remaining moves are all pawn moves.
    pawns = self.pawns & self.occupied_co[self.turn] & from_mask
    if not pawns:
        return

    # Generate pawn captures.
    capturers = pawns
    for from_square in scan_reversed(capturers):
        targets = (
            BB_PAWN_ATTACKS[self.turn][from_square] &
            self.occupied_co[not self.turn] & to_mask)

        for to_square in scan_reversed(targets):
            if square_rank(to_square) in [0, 7]:
                yield Move(from_square, to_square, QUEEN)
                yield Move(from_square, to_square, ROOK)
                yield Move(from_square, to_square, BISHOP)
                yield Move(from_square, to_square, KNIGHT)
            else:
                yield Move(from_square, to_square)

    # Prepare pawn advance generation.
    if self.turn == WHITE:
        single_moves = pawns << 8 & ~self.occupied
        double_moves = single_moves << 8 & ~self.occupied & (BB_RANK_3 | BB_RANK_4)
    else:
        single_moves = pawns >> 8 & ~self.occupied
        double_moves = single_moves >> 8 & ~self.occupied & (BB_RANK_6 | BB_RANK_5)

    single_moves &= to_mask
    double_moves &= to_mask

    # Generate single pawn moves.
    for to_square in scan_reversed(single_moves):
        from_square = to_square + (8 if self.turn == BLACK else -8)

        if square_rank(to_square) in [0, 7]:
            yield Move(from_square, to_square, QUEEN)
            yield Move(from_square, to_square, ROOK)
            yield Move(from_square, to_square, BISHOP)
            yield Move(from_square, to_square, KNIGHT)
        else:
            yield Move(from_square, to_square)

    # Generate double pawn moves.
    for to_square in scan_reversed(double_moves):
        from_square = to_square + (16 if self.turn == BLACK else -16)
        yield Move(from_square, to_square)

    # Generate en passant captures.
    if self.ep_square:
        yield from self.generate_pseudo_legal_ep(from_mask, to_mask)


def generate_legal_moves(self, from_mask: Bitboard = BB_ALL, to_mask: Bitboard = BB_ALL) -> Iterator[Move]:
    if self.is_variant_end():
        return

    king_mask = self.kings & self.occupied_co[self.turn]
    if king_mask:
        king = msb(king_mask)
        blockers = self._slider_blockers(king)
        checkers = self.attackers_mask(not self.turn, king)
        if checkers:
            for move in self._generate_evasions(king, checkers, from_mask, to_mask):
                if self._is_safe(king, blockers, move):
                    yield move
        else:
            for move in self.generate_pseudo_legal_moves(from_mask, to_mask):
                if self._is_safe(king, blockers, move):
                    yield move
    else:
        yield from self.generate_pseudo_legal_moves(from_mask, to_mask)