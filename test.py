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








from Client.client_V1_1 import Client_V1_1
import chess


chess_board = chess.Board()
list_k = chess_board._transposition_key()
for each in list_k:
    print(list(chess.scan_reversed(each)))