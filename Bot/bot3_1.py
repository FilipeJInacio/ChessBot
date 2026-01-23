import time
from Client.client import Client
import chess
from dataclasses import dataclass
from collections import defaultdict
import numpy as np

# Changes to position cost
# Added PeSTO
# Added king proximity evaluation
# Added enemy king proximity evaluation

@dataclass
class TTEntry:
    value: float
    depth: int
    flag: int  # EXACT, LOWERBOUND, UPPERBOUND
    best_move: chess.Move | None

EXACT = 0
LOWERBOUND = 1
UPPERBOUND = 2


class Bot3_1(Client):
    def __init__(self):
        super().__init__()

        self.weights = np.loadtxt("weights.txt")
        self.initialize_weights(self.weights)

        # Lookup table
        self.tt_1 = {} # position evaluation
        self.tt_2 = {} # alpha-beta pruning

        self.killer_moves = defaultdict(lambda: [None, None])

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
        phase = len(self.game.board.pieces(chess.KNIGHT, chess.WHITE)) + len(self.game.board.pieces(chess.KNIGHT, chess.BLACK)) + len(self.game.board.pieces(chess.BISHOP, chess.WHITE)) + len(self.game.board.pieces(chess.BISHOP, chess.BLACK)) + 2*(len(self.game.board.pieces(chess.ROOK, chess.WHITE)) + len(self.game.board.pieces(chess.ROOK, chess.BLACK))) + 4*(len(self.game.board.pieces(chess.QUEEN, chess.WHITE)) + len(self.game.board.pieces(chess.QUEEN, chess.BLACK)))/24

        feature = np.zeros(398*2+1)
        feature[0] = (len(self.game.board.pieces(chess.PAWN, chess.WHITE)) - len(self.game.board.pieces(chess.PAWN, chess.BLACK)))/8
        feature[1] = (len(self.game.board.pieces(chess.KNIGHT, chess.WHITE)) - len(self.game.board.pieces(chess.KNIGHT, chess.BLACK)))/2
        feature[2] = (len(self.game.board.pieces(chess.BISHOP, chess.WHITE)) - len(self.game.board.pieces(chess.BISHOP, chess.BLACK)))/2
        feature[3] = (len(self.game.board.pieces(chess.ROOK, chess.WHITE)) - len(self.game.board.pieces(chess.ROOK, chess.BLACK)))/2
        feature[4] = (len(self.game.board.pieces(chess.QUEEN, chess.WHITE)) - len(self.game.board.pieces(chess.QUEEN, chess.BLACK)))/2

        for square in self.game.board.pieces(chess.PAWN, chess.WHITE):
            feature[5 + square^56] += 1/8
        for square in self.game.board.pieces(chess.PAWN, chess.BLACK):
            feature[5 + square] -= 1/8

        for square in self.game.board.pieces(chess.KNIGHT, chess.WHITE):
            feature[69 + square^56] += 1/2
        for square in self.game.board.pieces(chess.KNIGHT, chess.BLACK):
            feature[69 + square] -= 1/2

        for square in self.game.board.pieces(chess.BISHOP, chess.WHITE):
            feature[133 + square^56] += 1/2
        for square in self.game.board.pieces(chess.BISHOP, chess.BLACK):
            feature[133 + square] -= 1/2

        for square in self.game.board.pieces(chess.ROOK, chess.WHITE):
            feature[197 + square^56] += 1/2
        for square in self.game.board.pieces(chess.ROOK, chess.BLACK):
            feature[197 + square] -= 1/2

        for square in self.game.board.pieces(chess.QUEEN, chess.WHITE):
            feature[261 + square^56] += 1
        for square in self.game.board.pieces(chess.QUEEN, chess.BLACK):
            feature[261 + square] -= 1

        for square in self.game.board.pieces(chess.KING, chess.WHITE): 
            feature[325 + square^56] += 1
        for square in self.game.board.pieces(chess.KING, chess.BLACK):
            feature[325 + square] -= 1


        temp = []
        turn = self.game.board.turn  # save the current turn

        self.game.board.turn = chess.WHITE
        legal_moves = list(self.game.board.legal_moves)
        temp.append(sum(1 for move in legal_moves if move.from_square in self.game.board.pieces(chess.PAWN, chess.WHITE)))
        temp.append(sum(1 for move in legal_moves if move.from_square in self.game.board.pieces(chess.KNIGHT, chess.WHITE)))
        temp.append(sum(1 for move in legal_moves if move.from_square in self.game.board.pieces(chess.BISHOP, chess.WHITE)))
        temp.append(sum(1 for move in legal_moves if move.from_square in self.game.board.pieces(chess.ROOK, chess.WHITE)))
        temp.append(sum(1 for move in legal_moves if move.from_square in self.game.board.pieces(chess.QUEEN, chess.WHITE)))
        temp.append(sum(1 for move in legal_moves if move.from_square in self.game.board.pieces(chess.KING, chess.WHITE)))

        self.game.board.turn = chess.BLACK
        legal_moves = list(self.game.board.legal_moves)
        temp.append(sum(1 for move in legal_moves if move.from_square in self.game.board.pieces(chess.PAWN, chess.BLACK)))
        temp.append(sum(1 for move in legal_moves if move.from_square in self.game.board.pieces(chess.KNIGHT, chess.BLACK)))
        temp.append(sum(1 for move in legal_moves if move.from_square in self.game.board.pieces(chess.BISHOP, chess.BLACK)))
        temp.append(sum(1 for move in legal_moves if move.from_square in self.game.board.pieces(chess.ROOK, chess.BLACK)))
        temp.append(sum(1 for move in legal_moves if move.from_square in self.game.board.pieces(chess.QUEEN, chess.BLACK)))
        temp.append(sum(1 for move in legal_moves if move.from_square in self.game.board.pieces(chess.KING, chess.BLACK)))
        self.game.board.turn = turn  # restore the original turn

        feature[389] = (temp[0] - temp[6])/(8*4)
        feature[390] = (temp[1] - temp[7])/(2*8)
        feature[391] = (temp[2] - temp[8])/(2*13)
        feature[392] = (temp[3] - temp[9])/(2*14)
        feature[393] = (temp[4] - temp[10])/(1*27)
        feature[394] = (temp[5] - temp[11])/(1*8)

        feature[395] = 1 if self.game.board.turn == chess.WHITE else -1

        # count passing pawns
        passing_pawns_white = 0
        passing_pawns_black = 0
        for square in self.game.board.pieces(chess.PAWN, chess.WHITE):
            file = chess.square_file(square)
            is_passing = True
            for enemy_square in self.game.board.pieces(chess.PAWN, chess.BLACK):
                enemy_file = chess.square_file(enemy_square)
                if abs(file - enemy_file) <= 1 and chess.square_rank(enemy_square) > chess.square_rank(square):
                    is_passing = False
                    break
            if is_passing:
                passing_pawns_white += 1

        for square in self.game.board.pieces(chess.PAWN, chess.BLACK):
            file = chess.square_file(square)
            is_passing = True
            for enemy_square in self.game.board.pieces(chess.PAWN, chess.WHITE):
                enemy_file = chess.square_file(enemy_square)
                if abs(file - enemy_file) <= 1 and chess.square_rank(enemy_square) < chess.square_rank(square):
                    is_passing = False
                    break
            if is_passing:
                passing_pawns_black += 1

        # count stacked pawns
        # basically, if 2 stacked +2 if 3 stacked +3 etc, if 2 stacked in 2 different files +4
        stacked_pawns_white = 0
        stacked_pawns_black = 0
        for file in range(8):
            count_white = 0
            count_black = 0
            for rank in range(8):
                square = chess.square(file, rank)
                if self.game.board.piece_at(square) == chess.Piece(chess.PAWN, chess.WHITE):
                    count_white += 1
                elif self.game.board.piece_at(square) == chess.Piece(chess.PAWN, chess.BLACK):
                    count_black += 1
            if count_white > 1:
                stacked_pawns_white += count_white
            if count_black > 1:
                stacked_pawns_black += count_black

        feature[396] = (passing_pawns_white - passing_pawns_black)/8
        feature[397] = (stacked_pawns_white - stacked_pawns_black)/8

        feature[398:796] = feature[0:398] * (1.0-phase)
        feature[0:398] *= phase

        white_king_square = list(self.game.board.pieces(chess.KING, chess.WHITE))[0]
        black_king_square = list(self.game.board.pieces(chess.KING, chess.BLACK))[0]
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

        return feature

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

        feature = self.get_feature_vector()

        score = np.dot(self.weights, feature)

        self.tt_1[key] = score
        return score
    
    def store_killer(self, depth, move):
        if move is None:
            return
        killers = self.killer_moves[depth]
        if move != killers[0]:
            killers[1] = killers[0]
            killers[0] = move

    def ordered_moves(self, key, depth):
        board = self.game.board
        tt_entry = self.tt_2.get(key)

        hash_move = tt_entry.best_move if tt_entry else None

        winning_caps = []
        losing_caps = []
        killers = []
        quiet = []

        for move in board.legal_moves:
            if move == hash_move:
                continue

            if board.is_capture(move):
                victim = board.piece_type_at(move.to_square)
                attacker = board.piece_type_at(move.from_square)
                if victim and attacker and victim >= attacker:
                    winning_caps.append(move)
                else:
                    losing_caps.append(move)

            elif move in self.killer_moves[depth]:
                killers.append(move)

            else:
                quiet.append(move)

        ordered = []
        if hash_move:
            ordered.append(hash_move)

        ordered.extend(winning_caps)
        ordered.extend(killers)
        ordered.extend(losing_caps)
        ordered.extend(quiet)

        return ordered

    def minimax(self, depth, alpha, beta, maximizing_player):
        board = self.game.board
        key = board._transposition_key()

        # TT lookup
        entry = self.tt_2.get(key)
        if entry and entry.depth >= depth:
            if entry.flag == EXACT:
                return entry.value
            elif entry.flag == LOWERBOUND:
                alpha = max(alpha, entry.value)
            elif entry.flag == UPPERBOUND:
                beta = min(beta, entry.value)
            if alpha >= beta:
                return entry.value

        if depth == 0 or self.game.is_game_over():
            value = self.position_evaluation()
            self.tt_2[key] = TTEntry(value, depth, EXACT, None)
            return value

        original_alpha = alpha
        best_move = None

        if maximizing_player:
            value = float("-inf")
            for move in self.ordered_moves(key, depth):
                self.game.board.push(move)
                new_value = self.minimax(depth - 1, alpha, beta, False)
                self.game.board.pop()
                
                if new_value > value:
                    value = new_value
                    best_move = move

                alpha = max(alpha, value)

                if beta <= alpha:
                    if not board.is_capture(move):
                        self.store_killer(depth, move)
                    break 
        else:
            value = float("inf")
            for move in self.ordered_moves(key, depth):
                self.game.board.push(move)
                new_value = self.minimax(depth - 1, alpha, beta, True)
                self.game.board.pop()

                if new_value < value:
                    value = new_value
                    best_move = move

                beta = min(beta, value)
                if beta <= alpha:
                    if not board.is_capture(move):
                        self.store_killer(depth, move)
                    break

        # Store in TT
        if value <= original_alpha:
            flag = UPPERBOUND
        elif value >= beta:
            flag = LOWERBOUND
        else:
            flag = EXACT

        self.tt_2[key] = TTEntry(value, depth, flag, best_move)
        return value
        
    def select_move(self):
        start_time = time.time()
        depth = 3
        best_move = None
        key = self.game.board._transposition_key()

        if self.game.board.turn == chess.WHITE:
            best_value = float("-inf")
            for move in self.ordered_moves(key, depth):
                self.game.board.push(move)
                value = self.minimax(depth - 1, float("-inf"), float("inf"), False)
                self.game.board.pop()
                if value > best_value:
                    best_value = value
                    best_move = move
        else:
            best_value = float("inf")
            for move in self.ordered_moves(key, depth):
                self.game.board.push(move)
                value = self.minimax(depth - 1, float("-inf"), float("inf"), True)
                self.game.board.pop()
                if value < best_value:
                    best_value = value
                    best_move = move

        # update weights file

        end_time = time.time()
        #print(f"Took {end_time - start_time:.2f} seconds")

        if best_move is None:
            # select a random move if no best move found
            best_move = list(self.game.board.legal_moves)[0]

        return best_move, end_time - start_time


