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