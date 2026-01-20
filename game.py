import chess

class ChessGame:
    def __init__(self, fen=None):
        self.board = chess.Board(fen) if fen else chess.Board()

        # Material evaluation
        self.piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0
        }

        # Positional evaluation
        self.knight_positional_bonus = [
            -0.5, -0.4, -0.3, -0.3, -0.3, -0.3, -0.4, -0.5,
            -0.4, -0.2, 0.00, 0.05, 0.05, 0.00, -0.2, -0.4,
            -0.3, 0.00, 0.15, 0.25, 0.25, 0.15, 0.00, -0.3,
            -0.3, 0.05, 0.25, 0.35, 0.35, 0.25, 0.05, -0.3,
            -0.3, 0.05, 0.25, 0.35, 0.35, 0.25, 0.05, -0.3,
            -0.3, 0.00, 0.15, 0.25, 0.25, 0.15, 0.00, -0.3,
            -0.4, -0.2, 0.00, 0.05, 0.05, 0.00, -0.2, -0.4,
            -0.5, -0.4, -0.3, -0.3, -0.3, -0.3, -0.4, -0.5
        ]

        self.knight_value_per_mobility = 0.04

        self.bishop_positional_bonus = [
            -0.30, -0.20, -0.20, -0.20, -0.20, -0.20, -0.20, -0.30,
            -0.20,  0.00,  0.05,  0.10,  0.10,  0.05,  0.00, -0.20,
            -0.20,  0.05,  0.10,  0.15,  0.15,  0.10,  0.05, -0.20,
            -0.20,  0.10,  0.15,  0.20,  0.20,  0.15,  0.10, -0.20,
            -0.20,  0.10,  0.15,  0.20,  0.20,  0.15,  0.10, -0.20,
            -0.20,  0.05,  0.10,  0.15,  0.15,  0.10,  0.05, -0.20,
            -0.20,  0.00,  0.05,  0.10,  0.10,  0.05,  0.00, -0.20,
            -0.30, -0.20, -0.20, -0.20, -0.20, -0.20, -0.20, -0.30
        ]

        self.bishop_value_per_mobility = 0.05

        self.rook_positional_bonus = [
             0.00,   0.00,   0.05,   0.10,   0.10,   0.05,   0.00,   0.00,
             0.20,   0.25,   0.30,   0.35,   0.35,   0.30,   0.25,   0.20,
             0.00,   0.05,   0.10,   0.15,   0.15,   0.10,   0.05,   0.00,
            -0.05,   0.00,   0.05,   0.10,   0.10,   0.05,   0.00,  -0.05,
            -0.05,   0.00,   0.05,   0.10,   0.10,   0.05,   0.00,  -0.05,
            -0.10,  -0.05,   0.00,   0.05,   0.05,   0.00,  -0.05,  -0.10,
            -0.10,  -0.05,   0.00,   0.05,   0.05,   0.00,  -0.05,  -0.10,
             0.00,   0.00,   0.05,   0.10,   0.10,   0.05,   0.00,   0.00
        ]

        self.rook_value_per_mobility = 0.03

        self.pawn_positional_bonus = [
            0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00,
            0.80,  0.80,  0.80,  0.90,  0.90,  0.80,  0.80,  0.80,
            0.30,  0.30,  0.40,  0.50,  0.50,  0.40,  0.30,  0.30,
            0.15,  0.15,  0.25,  0.35,  0.35,  0.25,  0.15,  0.15,
            0.05,  0.05,  0.15,  0.25,  0.25,  0.15,  0.05,  0.05,
            0.00,  0.00,  0.05,  0.15,  0.15,  0.05,  0.00,  0.00,
            0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00,
            0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00
        ] * 2

        self.queen_positional_bonus = [
            -0.20,  -0.10,  -0.10,  -0.05,  -0.05,  -0.10,  -0.10,  -0.20,
            -0.10,   0.00,   0.00,   0.00,   0.00,   0.00,   0.00,  -0.10,
            -0.10,   0.00,   0.05,   0.05,   0.05,   0.05,   0.00,  -0.10,
            -0.05,   0.00,   0.05,   0.10,   0.10,   0.05,   0.00,  -0.05,
            -0.05,   0.00,   0.05,   0.10,   0.10,   0.05,   0.00,  -0.05,
            -0.10,   0.00,   0.05,   0.05,   0.05,   0.05,   0.00,  -0.10,
            -0.10,   0.00,   0.00,   0.00,   0.00,   0.00,   0.00,  -0.10,
            -0.20,  -0.10,  -0.10,  -0.05,  -0.05,  -0.10,  -0.10,  -0.20
        ]

        self.queen_value_per_mobility = 0.02

        self.king_positional_bonus = [
            -0.60,  -0.70,  -0.70,  -0.80,  -0.80,  -0.70,  -0.70,  -0.60,
            -0.60,  -0.70,  -0.70,  -0.80,  -0.80,  -0.70,  -0.70,  -0.60,
            -0.50,  -0.60,  -0.60,  -0.70,  -0.70,  -0.60,  -0.60,  -0.50,
            -0.40,  -0.50,  -0.50,  -0.60,  -0.60,  -0.50,  -0.50,  -0.40,
            -0.30,  -0.40,  -0.40,  -0.50,  -0.50,  -0.40,  -0.40,  -0.30,
            -0.20,  -0.30,  -0.30,  -0.40,  -0.40,  -0.30,  -0.30,  -0.20,
            -0.10,  -0.20,  -0.20,  -0.30,  -0.30,  -0.20,  -0.20,  -0.10,
             0.20,   0.30,   0.10,  -0.10,  -0.10,   0.10,   0.30,   0.20
        ]

        self.king_value_per_mobility = 0.01

        self.enemy_king_positional_bonus = [
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 2, 3, 4, 4, 3, 2, 0,
            0, 2, 4, 5, 5, 4, 2, 0,
            0, 2, 3, 4, 4, 3, 2, 0,
            0, 1, 2, 2, 2, 2, 1, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0
        ]

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
        enemy_color = self.board.turn
        my_color = not enemy_color

        # Does the game have a winner?
        if self.is_game_over():
            winner = self.get_winner()
            if winner == my_color:
                return float('inf')
            elif winner == enemy_color:
                return float('-inf')
            else:
                return 0

        # Count material
        eval_score = 0
        for piece_type in self.piece_values:
            eval_score += len(self.board.pieces(piece_type, my_color)) * self.piece_values[piece_type]
            eval_score -= len(self.board.pieces(piece_type, enemy_color)) * self.piece_values[piece_type]

        moves = list(self.board.legal_moves)

        for square in chess.SQUARES:
            mobility = sum(1 for move in moves if move.from_square == square)
            piece = self.board.piece_at(square)
            if piece:
                if piece.piece_type == chess.KNIGHT:
                    if piece.color == my_color:
                        eval_score += self.knight_positional_bonus[square]
                        eval_score += self.knight_value_per_mobility * mobility
                    else:
                        eval_score -= self.knight_positional_bonus[square]
                        eval_score -= self.knight_value_per_mobility * mobility
                elif piece.piece_type == chess.BISHOP:
                    if piece.color == my_color:
                        eval_score += self.bishop_positional_bonus[square]
                        eval_score += self.bishop_value_per_mobility * mobility
                    else:
                        eval_score -= self.bishop_positional_bonus[square]
                        eval_score -= self.bishop_value_per_mobility * mobility
                elif piece.piece_type == chess.ROOK:
                    if my_color == chess.WHITE:
                        if piece.color == my_color:
                            eval_score += self.rook_positional_bonus[square]
                            eval_score += self.rook_value_per_mobility * mobility
                        else:
                            eval_score -= self.rook_positional_bonus[chess.square_mirror(square)]
                            eval_score -= self.rook_value_per_mobility * mobility
                    else:
                        if piece.color == my_color:
                            eval_score += self.rook_positional_bonus[chess.square_mirror(square)]
                            eval_score += self.rook_value_per_mobility * mobility
                        else:
                            eval_score -= self.rook_positional_bonus[square]
                            eval_score -= self.rook_value_per_mobility * mobility
                elif piece.piece_type == chess.PAWN:
                    if my_color == chess.WHITE:
                        if piece.color == my_color:
                            eval_score += self.pawn_positional_bonus[square]
                        else:
                            eval_score -= self.pawn_positional_bonus[chess.square_mirror(square)]
                    else:
                        if piece.color == my_color:
                            eval_score += self.pawn_positional_bonus[chess.square_mirror(square)]
                        else:
                            eval_score -= self.pawn_positional_bonus[square]
                elif piece.piece_type == chess.QUEEN:
                    if piece.color == my_color:
                        eval_score += self.queen_positional_bonus[square]
                        eval_score += self.queen_value_per_mobility * mobility
                    else:
                        eval_score -= self.queen_positional_bonus[square]
                        eval_score -= self.queen_value_per_mobility * mobility
                elif piece.piece_type == chess.KING:
                    if my_color == chess.WHITE:
                        if piece.color == my_color:
                            eval_score += self.king_positional_bonus[square]
                            eval_score += self.king_value_per_mobility * mobility
                        else:
                            eval_score -= self.king_positional_bonus[chess.square_mirror(square)]
                            eval_score -= self.king_value_per_mobility * mobility
                    else:
                        if piece.color == my_color:
                            eval_score += self.king_positional_bonus[chess.square_mirror(square)]
                            eval_score += self.king_value_per_mobility * mobility
                        else:
                            eval_score -= self.king_positional_bonus[square]
                            eval_score -= self.king_value_per_mobility * mobility

        # move the king closer to the enemy king
        # Calculate the distance
        # Value increases as the opponent has less pieces
                

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