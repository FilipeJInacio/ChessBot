from Client.client import Client
import chess

# bugged

class Client_minmax(Client):
    def __init__(self):
        super().__init__()
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

    def position_evaluation(self):
        enemy_color = self.game.board.turn
        my_color = not enemy_color

        # Does the game have a winner?
        if self.game.is_game_over():
            winner = self.game.get_winner()
            if winner == my_color:
                return float('inf')
            elif winner == enemy_color:
                return float('-inf')
            else:
                return 0

        # Count material
        eval_score = 0
        for piece_type in self.piece_values:
            eval_score += len(self.game.board.pieces(piece_type, my_color)) * self.piece_values[piece_type]
            eval_score -= len(self.game.board.pieces(piece_type, enemy_color)) * self.piece_values[piece_type]

        moves = list(self.game.board.legal_moves)

        for square in chess.SQUARES:
            mobility = sum(1 for move in moves if move.from_square == square)
            piece = self.game.board.piece_at(square)
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

    def minimax(self, depth, maximizing_player):
        # Terminal condition
        if depth == 0 or self.game.is_game_over():
            return self.position_evaluation()

        if maximizing_player:
            max_value = float("-inf")
            for move in self.game.get_possible_moves():
                # Simulate the move
                self.game.make_move(move)
                value = self.minimax(depth - 1, False)
                self.game.undo_move()
                max_value = max(max_value, value)
            return max_value
        else:
            min_value = float("inf")
            for move in self.game.get_possible_moves():
                self.game.make_move(move)
                value = self.minimax(depth - 1, True)
                self.game.undo_move()
                min_value = min(min_value, value)
            return min_value

    def select_move(self):
        depth = 3
        best_value = float("-inf")
        best_move = None

        for move in self.game.get_possible_moves():
            self.game.make_move(move)
            value = self.minimax(depth - 1, False)
            self.game.undo_move()
            if value > best_value:
                best_value = value
                best_move = move

        return best_move


