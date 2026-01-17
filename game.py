import chess

class ChessGame:
    def __init__(self, fen=None):
        self.board = chess.Board(fen) if fen else chess.Board()

    def get_possible_moves(self):
        return [move.uci() for move in self.board.legal_moves]

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
        return eval_score

    def is_game_over(self):
        return self.board.is_game_over()

    def get_winner(self):
        if self.board.is_checkmate():
            return 'Black' if self.board.turn == chess.WHITE else 'White'
        return None

    def get_board_fen(self):
        return self.board.fen()
    
    def from_fen(self, fen):
        self.board.set_fen(fen)

