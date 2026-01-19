import chess

class ChessGame:
    def __init__(self, fen=None):
        self.board = chess.Board(fen) if fen else chess.Board()

    def reset(self):
        self.board.reset()




    def get_possible_moves(self):
        return [move.uci() for move in self.board.legal_moves]

    def get_last_move(self):
        if self.board.move_stack:
            return self.board.peek()
        return None




    def make_move(self, move_uci):
        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                self.board.push(move)
                return True
            else:
                return False
        except ValueError:
            return False

    def undo_move(self):
        if self.board.move_stack:
            self.board.pop()
            return True
        return False
    



    def position_evaluation(self):
        # Simple material evaluation
        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0
        }
        eval_score = 0
        for piece_type in piece_values:
            eval_score += len(self.board.pieces(piece_type, chess.WHITE)) * piece_values[piece_type]
            eval_score -= len(self.board.pieces(piece_type, chess.BLACK)) * piece_values[piece_type]

        # Positional evaluation (very basic)
        knight_positional_bonus = [
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 2, 3, 4, 4, 3, 2, 0,
            0, 2, 4, 5, 5, 4, 2, 0,
            0, 2, 3, 4, 4, 3, 2, 0,
            0, 1, 2, 2, 2, 2, 1, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0
        ]

        bishop_positional_bonus = [
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 2, 3, 4, 4, 3, 2, 0,
            0, 2, 4, 5, 5, 4, 2, 0,
            0, 2, 3, 4, 4, 3, 2, 0,
            0, 1, 2, 2, 2, 2, 1, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0
        ]

        rook_positional_bonus = [
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 2, 3, 4, 4, 3, 2, 0,
            0, 2, 4, 5, 5, 4, 2, 0,
            0, 2, 3, 4, 4, 3, 2, 0,
            0, 1, 2, 2, 2, 2, 1, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0
        ]

        pawn_positional_bonus = [
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 2, 3, 4, 4, 3, 2, 0,
            0, 2, 4, 5, 5, 4, 2, 0,
            0, 2, 3, 4, 4, 3, 2, 0,
            0, 1, 2, 2, 2, 2, 1, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0
        ]

        queen_positional_bonus = [
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 2, 3, 4, 4, 3, 2, 0,
            0, 2, 4, 5, 5, 4, 2, 0,
            0, 2, 3, 4, 4, 3, 2, 0,
            0, 1, 2, 2, 2, 2, 1, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0
        ]

        king_positional_bonus = [
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 2, 3, 4, 4, 3, 2, 0,
            0, 2, 4, 5, 5, 4, 2, 0,
            0, 2, 3, 4, 4, 3, 2, 0,
            0, 1, 2, 2, 2, 2, 1, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0
        ]

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece and piece.piece_type == chess.KNIGHT:
                if piece.color == chess.WHITE:
                    eval_score += knight_positional_bonus[square]
                else:
                    eval_score -= knight_positional_bonus[chess.square_mirror(square)]


        # degrees of freedom bonus
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                moves = list(self.board.legal_moves)
                freedom = sum(1 for move in moves if move.from_square == square)
                if piece.color == chess.WHITE:
                    eval_score += 0.1 * freedom
                else:
                    eval_score -= 0.1 * freedom
        


        return eval_score




    def turn(self):
        return 'White' if self.board.turn == chess.WHITE else 'Black'

    def is_game_over(self):
        return self.board.is_checkmate() or self.board.is_stalemate() or self.board.is_insufficient_material() or self.board.can_claim_fifty_moves() or self.board.can_claim_threefold_repetition()

    def game_over_reason(self):
        if self.board.is_checkmate():
            return 'checkmate'
        elif self.board.is_stalemate():
            return 'stalemate'
        elif self.board.is_insufficient_material():
            return 'insufficient_material'
        elif self.board.can_claim_fifty_moves():
            return 'fifty_moves_rule'
        elif self.board.can_claim_threefold_repetition():
            return 'threefold_repetition'
        else:
            return None

    def get_winner(self):
        if self.board.is_checkmate():
            return 'Black' if self.board.turn == chess.WHITE else 'White'
        return None




    def get_board_fen(self):
        return self.board.fen()
    
    def from_fen(self, fen):
        self.board.set_fen(fen)



    def print_board(self):
        print("=======================")
        print(self.board)
        print("=======================")