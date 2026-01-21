import time
from Client.client import Client
import chess

# Negamax

# WHITE: 
# BLACK: 

# TODO
# move king to help with checkmate
# positioning bonus should transition to end game bonus
# calculate distance from own king to enemy king in end game

# Use last move to optimize evaluation (only compute changes)

# Piece–square tables
# Mobility (already partly done)
# King safety
# Pawn structure (isolated, doubled, passed pawns)
# Tempo / side to move


class Client_V1_3(Client):
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

        self.knight_positional_bonus_transposed = [
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

        

        self.queen_value_per_mobility = 0.02
        self.knight_value_per_mobility = 0.04
        self.bishop_value_per_mobility = 0.05
        self.rook_value_per_mobility = 0.03
        self.king_value_per_mobility = 0.01

    def position_evaluation(self):
        board = self.game.board
        key = board._transposition_key()
        if key in self.tt_1:
            return self.tt_1[key]
        
        my_color = board.turn     # swapped because of negamax
        enemy_color = not my_color

        # Terminal positions
        if board.is_game_over():
            winner = self.game.get_winner()
            if winner == my_color:
                score = float('inf')
            elif winner == enemy_color:
                score = float('-inf')
            else:
                score = 0
            self.tt_1[key] = score
            return score

        eval_score = 0

        for piece_type in chess.PIECE_TYPES:
            value = self.piece_values[piece_type]
            table = self.psqt[piece_type]

            # My pieces
            for square in board.pieces(piece_type, my_color):
                idx = square if my_color == chess.BLACK else square ^ 56
                eval_score += value + table[idx]

            # Enemy pieces
            for square in board.pieces(piece_type, enemy_color):
                idx = square if enemy_color == chess.BLACK else square ^ 56
                eval_score -= value + table[idx]
                
        self.tt_1[key] = eval_score
        return eval_score

    def negamax(self, depth, alpha, beta):
        # Terminal condition
        if depth == 0 or self.game.is_game_over():
            return self.position_evaluation()

        value = float("-inf")

        for move in self.game.get_possible_moves():
            self.game.make_move(move)
            score = -self.negamax(depth - 1, -beta, -alpha)
            self.game.undo_move()

            value = max(value, score)
            alpha = max(alpha, value)

            if alpha >= beta:
                break  # alpha-beta cutoff

        return value
        
    def select_move(self):
        start_time = time.time()
        depth = 3
        best_value = float("-inf")
        best_move = None

        for move in self.game.get_possible_moves():
            self.game.make_move(move)
            value = -self.negamax(depth - 1, float("-inf"), float("inf"))
            self.game.undo_move()

            if value > best_value:
                best_value = value
                best_move = move

        end_time = time.time()
        print(f"Took {end_time - start_time:.2f} seconds")

        return best_move, end_time - start_time


