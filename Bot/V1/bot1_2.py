import time
from Client.client import Client
import chess

# NEGAMAX with alpha-beta pruning and transposition table and basic positional evaluation
# Improvement: Speed up? Simplification





class Bot1_2(Client):
    def __init__(self):
        super().__init__()

        # Lookup table
        self.tt_1 = {} # position evaluation

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
            -0.3, 0.00, 0.15, 0.20, 0.20, 0.15, 0.00, -0.3,
            -0.3, 0.05, 0.20, 0.25, 0.25, 0.20, 0.05, -0.3,
            -0.3, 0.05, 0.20, 0.25, 0.25, 0.20, 0.05, -0.3,
            -0.3, 0.00, 0.15, 0.20, 0.20, 0.15, 0.00, -0.3,
            -0.4, -0.2, 0.00, 0.05, 0.05, 0.00, -0.2, -0.4,
            -0.5, -0.4, -0.3, -0.3, -0.3, -0.3, -0.4, -0.5
        ]

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

        self.rook_positional_bonus = [
             0.00,   0.00,   0.05,   0.10,   0.10,   0.05,   0.00,   0.00,
             0.20,   0.25,   0.30,   0.35,   0.35,   0.30,   0.25,   0.20,
             0.00,   0.05,   0.10,   0.15,   0.15,   0.10,   0.05,   0.00,
            -0.05,   0.00,   0.05,   0.10,   0.10,   0.05,   0.00,  -0.05,
            -0.05,   0.00,   0.05,   0.10,   0.10,   0.05,   0.00,  -0.05,
            -0.10,  -0.05,   0.00,   0.05,   0.05,   0.00,  -0.05,  -0.10,
            -0.10,  -0.05,   0.00,   0.05,   0.05,   0.00,  -0.05,  -0.10,
             0.00,   0.00,   0.05,   0.10,   0.10,   0.05,   0.00,   0.00,
        ]

        self.pawn_positional_bonus = [
            0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00,
            0.80,  0.80,  0.80,  0.90,  0.90,  0.80,  0.80,  0.80,
            0.30,  0.30,  0.40,  0.50,  0.50,  0.40,  0.30,  0.30,
            0.15,  0.15,  0.25,  0.35,  0.35,  0.25,  0.15,  0.15,
            0.05,  0.05,  0.15,  0.25,  0.25,  0.15,  0.05,  0.05,
            0.00,  0.00,  0.05,  0.15,  0.15,  0.05,  0.00,  0.00,
            0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00,
            0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00
        ]

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

        self.psqt = {
            chess.PAWN: self.pawn_positional_bonus,
            chess.KNIGHT: self.knight_positional_bonus,
            chess.BISHOP: self.bishop_positional_bonus,
            chess.ROOK: self.rook_positional_bonus,
            chess.QUEEN: self.queen_positional_bonus,
            chess.KING: self.king_positional_bonus,
        }

    def position_evaluation(self):
        board = self.game.board
        key = board._transposition_key()
        if key in self.tt_1:
            return self.tt_1[key]
        
        if board.is_game_over():
            winner = self.game.get_winner()
            if winner == chess.WHITE:
                score = float('inf')
            elif winner == chess.BLACK:
                score = float('-inf')
            else:
                score = 0
            self.tt_1[key] = score
            return score

        eval_score = 0

        for piece_type in chess.PIECE_TYPES:
            value = self.piece_values[piece_type]
            table = self.psqt[piece_type]

            for square in board.pieces(piece_type, chess.WHITE):
                eval_score += value + table[square ^ 56]

            for square in board.pieces(piece_type, chess.BLACK):
                eval_score -= value + table[square]
                
        self.tt_1[key] = eval_score
        return eval_score

    def negamax(self, depth, alpha, beta, turn_multiplier):
        # Terminal condition
        if depth == 0 or self.game.is_game_over():
            return turn_multiplier * self.position_evaluation()

        value = float("-inf")

        for move in self.game.get_possible_moves():
            self.game.make_move(move)
            score = -self.negamax(depth - 1, -beta, -alpha, -turn_multiplier)
            self.game.undo_move()

            value = max(value, score)
            alpha = max(alpha, value)

            if alpha >= beta:
                break  # alpha-beta cutoff

        return value
        
    def select_move(self):
        start_time = time.time()
        depth = 4
        best_move = None
        best_value = float("-inf")

        for move in self.game.get_possible_moves():
            self.game.make_move(move)
            value = -self.negamax(depth - 1, float("-inf"), float("inf"), 1 if self.game.board.turn == chess.WHITE else -1)
            self.game.undo_move()
            if value > best_value:
                best_value = value
                best_move = move


        end_time = time.time()
        print(f"Took {end_time - start_time:.2f} seconds")

        return best_move, end_time - start_time


