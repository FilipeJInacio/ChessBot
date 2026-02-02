from Client.client import Client
import chess
import numpy as np

# Removed Transposition Table related code



class Bot3_2(Client):
    def __init__(self):
        super().__init__()

        self.tt = {} # Feature vector

        self.weights = np.loadtxt("weights.txt")
        self.initialize_weights(self.weights)

    def initialize_weights(self, weights):
        self.weights = weights 

        self.mg_value = {
            chess.PAWN:   self.weights[0],
            chess.KNIGHT: self.weights[1],
            chess.BISHOP: self.weights[2],
            chess.ROOK:   self.weights[3],
            chess.QUEEN:  self.weights[4],
        }

        self.eg_value = {
            chess.PAWN:   self.weights[398],
            chess.KNIGHT: self.weights[399],
            chess.BISHOP: self.weights[400],
            chess.ROOK:   self.weights[401],
            chess.QUEEN:  self.weights[402],
            chess.KING:   self.weights[403]
        }

        self.phase_weight = {
            chess.PAWN:   0,
            chess.KNIGHT: 1,
            chess.BISHOP: 1,
            chess.ROOK:   2,
            chess.QUEEN:  4,
            chess.KING:   0
        }

        self.MAX_PHASE = 24

        self.mg_pawn = self.weights[5:69].tolist()

        self.eg_pawn = self.weights[403:467].tolist()

        self.mg_knight = self.weights[69:133].tolist()

        self.eg_knight = self.weights[467:531].tolist()

        self.mg_bishop = self.weights[133:197].tolist()

        self.eg_bishop = self.weights[531:595].tolist()

        self.mg_rook = self.weights[197:261].tolist()

        self.eg_rook = self.weights[595:659].tolist()

        self.mg_queen = self.weights[261:325].tolist()

        self.eg_queen = self.weights[659:723].tolist()

        self.mg_king = self.weights[325:389].tolist()

        self.eg_king = self.weights[723:787].tolist()

        self.mg_psqt = {
            chess.PAWN: self.mg_pawn,
            chess.KNIGHT: self.mg_knight,
            chess.BISHOP: self.mg_bishop,
            chess.ROOK: self.mg_rook,
            chess.QUEEN: self.mg_queen,
            chess.KING: self.mg_king
        }

        self.eg_psqt = {
            chess.PAWN: self.eg_pawn,
            chess.KNIGHT: self.eg_knight,
            chess.BISHOP: self.eg_bishop,
            chess.ROOK: self.eg_rook,
            chess.QUEEN: self.eg_queen,
            chess.KING: self.eg_king
        }

        self.mg_tempo = self.weights[395]
        self.eg_tempo = self.weights[793]

        self.mg_mobility = self.weights[389:395].tolist()
        self.eg_mobility = self.weights[787:793].tolist()

        self.mg_pawn_structure = self.weights[396:398].tolist()
        self.eg_pawn_structure = self.weights[794:796].tolist()

        self.MAX_KING_DIST = 14  # max Manhattan distance on board
        self.eg_king_dist_weight = self.weights[796]

    def get_feature_vector(self):
        board = self.game.board
        key = board._transposition_key()
        if key in self.tt:
            return self.tt[key]

        pieces = {
            (chess.PAWN, chess.WHITE): board.pieces(chess.PAWN, chess.WHITE),
            (chess.PAWN, chess.BLACK): board.pieces(chess.PAWN, chess.BLACK),
            (chess.KNIGHT, chess.WHITE): board.pieces(chess.KNIGHT, chess.WHITE),
            (chess.KNIGHT, chess.BLACK): board.pieces(chess.KNIGHT, chess.BLACK),
            (chess.BISHOP, chess.WHITE): board.pieces(chess.BISHOP, chess.WHITE),
            (chess.BISHOP, chess.BLACK): board.pieces(chess.BISHOP, chess.BLACK),
            (chess.ROOK, chess.WHITE): board.pieces(chess.ROOK, chess.WHITE),
            (chess.ROOK, chess.BLACK): board.pieces(chess.ROOK, chess.BLACK),
            (chess.QUEEN, chess.WHITE): board.pieces(chess.QUEEN, chess.WHITE),
            (chess.QUEEN, chess.BLACK): board.pieces(chess.QUEEN, chess.BLACK),
            (chess.KING, chess.WHITE): board.pieces(chess.KING, chess.WHITE),
            (chess.KING, chess.BLACK): board.pieces(chess.KING, chess.BLACK),
        }

        phase_raw = (
            len(pieces[chess.KNIGHT, chess.WHITE]) + len(pieces[chess.KNIGHT, chess.BLACK]) +
            len(pieces[chess.BISHOP, chess.WHITE]) + len(pieces[chess.BISHOP, chess.BLACK]) +
            2 * (len(pieces[chess.ROOK, chess.WHITE]) + len(pieces[chess.ROOK, chess.BLACK])) +
            4 * (len(pieces[chess.QUEEN, chess.WHITE]) + len(pieces[chess.QUEEN, chess.BLACK]))
        )

        phase = phase_raw / 24.0

        feature = np.zeros(797, dtype=np.float32)

        feature[0] = (len(pieces[chess.PAWN, chess.WHITE]) - len(pieces[chess.PAWN, chess.BLACK])) / 8
        feature[1] = (len(pieces[chess.KNIGHT, chess.WHITE]) - len(pieces[chess.KNIGHT, chess.BLACK])) / 2
        feature[2] = (len(pieces[chess.BISHOP, chess.WHITE]) - len(pieces[chess.BISHOP, chess.BLACK])) / 2
        feature[3] = (len(pieces[chess.ROOK, chess.WHITE]) - len(pieces[chess.ROOK, chess.BLACK])) / 2
        feature[4] = (len(pieces[chess.QUEEN, chess.WHITE]) - len(pieces[chess.QUEEN, chess.BLACK])) / 1

        def add_piece_squares(offset, squares, value, flip):
            for sq in squares:
                feature[offset + (sq ^ 56 if flip else sq)] += value

        add_piece_squares(5,   pieces[chess.PAWN, chess.WHITE],   1/8, True)
        add_piece_squares(5,   pieces[chess.PAWN, chess.BLACK],  -1/8, False)

        add_piece_squares(69,  pieces[chess.KNIGHT, chess.WHITE],  1/2, True)
        add_piece_squares(69,  pieces[chess.KNIGHT, chess.BLACK], -1/2, False)

        add_piece_squares(133, pieces[chess.BISHOP, chess.WHITE],  1/2, True)
        add_piece_squares(133, pieces[chess.BISHOP, chess.BLACK], -1/2, False)

        add_piece_squares(197, pieces[chess.ROOK, chess.WHITE],    1/2, True)
        add_piece_squares(197, pieces[chess.ROOK, chess.BLACK],   -1/2, False)

        add_piece_squares(261, pieces[chess.QUEEN, chess.WHITE],   1.0, True)
        add_piece_squares(261, pieces[chess.QUEEN, chess.BLACK],  -1.0, False)

        add_piece_squares(325, pieces[chess.KING, chess.WHITE],    1.0, True)
        add_piece_squares(325, pieces[chess.KING, chess.BLACK],   -1.0, False)

        def mobility(color):
            board.turn = color
            counts = [0]*6
            for move in board.legal_moves:
                piece = board.piece_type_at(move.from_square)
                counts[piece - 1] += 1
            return counts
        
        turn = board.turn
        w = mobility(chess.WHITE)
        b = mobility(chess.BLACK)
        board.turn = turn

        feature[389] = (w[0] - b[0]) / (8*4)
        feature[390] = (w[1] - b[1]) / (2*8)
        feature[391] = (w[2] - b[2]) / (2*13)
        feature[392] = (w[3] - b[3]) / (2*14)
        feature[393] = (w[4] - b[4]) / (1*27)
        feature[394] = (w[5] - b[5]) / (1*8)

        feature[395] = 1 if board.turn == chess.WHITE else -1

        # count passing pawns
        white_pawns = list(board.pieces(chess.PAWN, chess.WHITE))
        black_pawns = list(board.pieces(chess.PAWN, chess.BLACK))

        white_pawns_by_file = [[] for _ in range(8)]
        black_pawns_by_file = [[] for _ in range(8)]

        for sq in white_pawns:
            white_pawns_by_file[chess.square_file(sq)].append(chess.square_rank(sq))

        for sq in black_pawns:
            black_pawns_by_file[chess.square_file(sq)].append(chess.square_rank(sq))

        passing_pawns_white = 0
        passing_pawns_black = 0

        # ---- White passing pawns ----
        for f in range(8):
            for r in white_pawns_by_file[f]:
                is_passing = True
                for ef in (f - 1, f, f + 1):
                    if 0 <= ef < 8:
                        if any(br > r for br in black_pawns_by_file[ef]):
                            is_passing = False
                            break
                if is_passing:
                    passing_pawns_white += 1

        # ---- Black passing pawns ----
        for f in range(8):
            for r in black_pawns_by_file[f]:
                is_passing = True
                for ef in (f - 1, f, f + 1):
                    if 0 <= ef < 8:
                        if any(wr < r for wr in white_pawns_by_file[ef]):
                            is_passing = False
                            break
                if is_passing:
                    passing_pawns_black += 1

        # count stacked pawns
        # basically, if 2 stacked +2 if 3 stacked +3 etc, if 2 stacked in 2 different files +4
        stacked_pawns_white = 0
        stacked_pawns_black = 0

        for f in range(8):
            cw = len(white_pawns_by_file[f])
            cb = len(black_pawns_by_file[f])

            if cw > 1:
                stacked_pawns_white += cw
            if cb > 1:
                stacked_pawns_black += cb

        feature[396] = (passing_pawns_white - passing_pawns_black)/8
        feature[397] = (stacked_pawns_white - stacked_pawns_black)/8

        feature[398:796] = feature[:398] * (1 - phase)
        feature[:398] *= phase

        white_king_square = list(board.pieces(chess.KING, chess.WHITE))[0]
        black_king_square = list(board.pieces(chess.KING, chess.BLACK))[0]
        white_king_file = chess.square_file(white_king_square)
        white_king_rank = chess.square_rank(white_king_square)
        black_king_file = chess.square_file(black_king_square)
        black_king_rank = chess.square_rank(black_king_square)
        feature[796] = 1 - 2*(14 - (abs(white_king_file - black_king_file) + abs(white_king_rank - black_king_rank)))/14

        # scaling factors
        feature[325:389] *= 0.2
        feature[723:787] *= 0.2
        feature[389:395] *= 0.1
        feature[787:793] *= 0.1
        feature[395:396] *= 0.05
        feature[793:794] *= 0.05
        feature[796] *= 0.1

        self.tt[key] = feature
        return feature

    def position_evaluation(self):
        board = self.game.board

        if board.is_game_over():
            winner = self.game.get_winner()
            if winner == chess.WHITE:
                score = float('inf')
            elif winner == chess.BLACK:
                score = float('-inf')
            else:
                score = 0
            return score

        feature = self.get_feature_vector()

        score = np.dot(self.weights, feature)
        return score

    def minimax(self, depth, alpha, beta, maximizing_player):
        board = self.game.board

        if depth == 0 or self.game.is_game_over():
            return self.position_evaluation()

        if maximizing_player:
            value = float("-inf")
            for move in list(board.legal_moves):
                self.game.board.push(move)
                new_value = self.minimax(depth - 1, alpha, beta, False)
                self.game.board.pop()
                
                value = max(value, new_value)
                alpha = max(alpha, value)

                if beta <= alpha:
                    break 
        else:
            value = float("inf")
            for move in list(board.legal_moves):
                self.game.board.push(move)
                new_value = self.minimax(depth - 1, alpha, beta, True)
                self.game.board.pop()

                value = min(value, new_value)
                beta = min(beta, value)
                if beta <= alpha:
                    break

        return value
        
    def select_move(self):
        depth = 3
        best_move = None

        if self.game.board.turn == chess.WHITE:
            best_value = float("-inf")
            for move in list(self.game.board.legal_moves):
                self.game.board.push(move)
                value = self.minimax(depth - 1, float("-inf"), float("inf"), False)
                self.game.board.pop()
                if value > best_value:
                    best_value = value
                    best_move = move
        else:
            best_value = float("inf")
            for move in list(self.game.board.legal_moves):
                self.game.board.push(move)
                value = self.minimax(depth - 1, float("-inf"), float("inf"), True)
                self.game.board.pop()
                if value < best_value:
                    best_value = value
                    best_move = move

        if best_move is None:
            # select a random move if no best move found
            best_move = list(self.game.board.legal_moves)[0]

        return best_move, None


