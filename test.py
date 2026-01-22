# 7 | 56 57 58 59 60 61 62 63
# 6 | 48 49 50 51 52 53 54 55
# 5 | 40 41 42 43 44 45 46 47
# 4 | 32 33 34 35 36 37 38 39
# 3 | 24 25 26 27 28 29 30 31
# 2 | 16 17 18 19 20 21 22 23
# 1 |  8  9 10 11 12 13 14 15
# 0 |  0  1  2  3  4  5  6  7
#      a  b  c  d  e  f  g  h

# normal search goes 0..7, 8..15, ..., 56..63
# flipped search goes 56..63, 48..55, ..., 0..7

# unidirectional white table, white to evaluate: 0 -> 56 
# unidirectional white table, black to evaluate: 56
# unidirectional black table, white to evaluate: 0
# unidirectional black table, black to evaluate: 56 -> 0


import time

def deep_search(board, depth):
    if depth == 0:
        return board.legal_moves.count()

    score = 0   
    for move in board.legal_moves:
        board.push(move)
        score += deep_search(board, depth - 1)
        board.pop()
    return score


import chess

chess_board = chess.Board()

depth = 4

start_time = time.time()
nodes = deep_search(chess_board, depth)
end_time = time.time()

elapsed_time = end_time - start_time

print(f"Depth: {depth}, Nodes: {nodes}, Time: {elapsed_time:.2f} seconds, Nodes/sec: {nodes/elapsed_time:.2f}")