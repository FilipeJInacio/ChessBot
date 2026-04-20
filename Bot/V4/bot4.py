from Client.client import Client
import chess
import numpy as np
from Bot.V4.model import ChessResNet
import torch

class Bot4(Client):
    def __init__(self):
        super().__init__()

        self.model = ChessResNet()
        self.model.load_state_dict(torch.load("Bot/V4/best_model.pt"))

    def get_feature_vector(self):
        board = self.game.board
        features = np.zeros(787, dtype=np.float32)

        # --- Piece planes [0:768] ---
        piece_order = [
            (chess.KING,   chess.WHITE),   # [0:64]
            (chess.QUEEN,  chess.WHITE),   # [64:128]
            (chess.ROOK,   chess.WHITE),   # [128:192]
            (chess.BISHOP, chess.WHITE),   # [192:256]
            (chess.KNIGHT, chess.WHITE),   # [256:320]
            (chess.PAWN,   chess.WHITE),   # [320:384]
            (chess.KING,   chess.BLACK),   # [384:448]
            (chess.QUEEN,  chess.BLACK),   # [448:512]
            (chess.ROOK,   chess.BLACK),   # [512:576]
            (chess.BISHOP, chess.BLACK),   # [576:640]
            (chess.KNIGHT, chess.BLACK),   # [640:704]
            (chess.PAWN,   chess.BLACK),   # [704:768]
        ]

        for i, (piece_type, color) in enumerate(piece_order):
            for square in board.pieces(piece_type, color):
                features[i * 64 + square] = 1.0

        # --- Castling rights [768:772] ---
        features[768] = float(board.has_kingside_castling_rights(chess.WHITE))
        features[769] = float(board.has_queenside_castling_rights(chess.WHITE))
        features[770] = float(board.has_kingside_castling_rights(chess.BLACK))
        features[771] = float(board.has_queenside_castling_rights(chess.BLACK))

        # --- En passant [772:780] ---
        if board.ep_square is not None:
            ep_file = chess.square_file(board.ep_square)  # 0-7
            features[772 + ep_file] = 1.0

        # --- Side to move [780] ---
        features[780] = float(board.turn == chess.WHITE)

        # --- Halfmove clock [781:785] ---
        # Encode as 4 bits (supports up to 100 moves for 50-move rule)
        halfmove = min(board.halfmove_clock, 15)  # cap at 15 for 4 bits
        for bit in range(4):
            features[781 + bit] = float((halfmove >> bit) & 1)

        # --- Repetition count [785:787] ---
        features[785] = float(board.is_repetition(2))
        features[786] = float(board.is_repetition(3))

        return torch.tensor(features).unsqueeze(0) # (1, 787)

    def position_evaluation(self):
        board = self.game.board

        if board.is_game_over():
            winner = chess.WHITE if board.result() == '1-0' else chess.BLACK if board.result() == '0-1' else None
            if winner == chess.WHITE:
                score = float('inf')
            elif winner == chess.BLACK:
                score = float('-inf')
            else:
                score = 0
            return score

        feature = self.get_feature_vector()
        score = self.model.predict_value(feature).item()
        return score

    def minimax(self, depth, alpha, beta, maximizing_player):
        board = self.game.board

        if depth == 0 or board.is_game_over():
            return self.position_evaluation()

        if maximizing_player:
            value = float("-inf")
            for move in list(board.legal_moves):
                board.push(move)
                new_value = self.minimax(depth - 1, alpha, beta, False)
                board.pop()
                
                value = max(value, new_value)
                alpha = max(alpha, value)

                if beta <= alpha:
                    break 
        else:
            value = float("inf")
            for move in list(board.legal_moves):
                board.push(move)
                new_value = self.minimax(depth - 1, alpha, beta, True)
                board.pop()

                value = min(value, new_value)
                beta = min(beta, value)
                if beta <= alpha:
                    break

        return value
        
    def select_move(self):
        depth = 2
        best_move = None
        board = self.game.board

        if board.turn == chess.WHITE:
            best_value = float("-inf")
            for move in list(board.legal_moves):
                board.push(move)
                value = self.minimax(depth - 1, float("-inf"), float("inf"), False)
                board.pop()
                if value > best_value:
                    best_value = value
                    best_move = move
        else:
            best_value = float("inf")
            for move in list(board.legal_moves):
                board.push(move)
                value = self.minimax(depth - 1, float("-inf"), float("inf"), True)
                board.pop()
                if value < best_value:
                    best_value = value
                    best_move = move

        if best_move is None:
            # select a random move if no best move found
            best_move = list(board.legal_moves)[0]

        return best_move, 0


