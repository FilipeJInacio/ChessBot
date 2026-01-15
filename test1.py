from dataclasses import dataclass
from typing import List, Optional, Tuple

Position = Tuple[int, int]


@dataclass
class Move:
    start: Position
    end: Position
    promotion: Optional[str] = None
    is_castling: bool = False
    is_en_passant: bool = False


class ChessMoveGenerator:
    def __init__(self, fen: str):
        self.board, self.turn, self.castling, self.en_passant = self.parse_fen(fen)

    # ---------------- FEN ---------------- #

    def parse_fen(self, fen: str):
        parts = fen.split()
        rows = parts[0].split('/')
        board = [[None for _ in range(8)] for _ in range(8)]

        for r, row in enumerate(rows):
            c = 0
            for ch in row:
                if ch.isdigit():
                    c += int(ch)
                else:
                    board[r][c] = ch
                    c += 1

        turn = parts[1]
        castling = parts[2]
        en_passant = None if parts[3] == "-" else self.square_to_pos(parts[3])

        return board, turn, castling, en_passant

    def square_to_pos(self, sq: str) -> Position:
        file = ord(sq[0]) - ord('a')
        rank = 8 - int(sq[1])
        return (rank, file)

    def pos_to_square(self, pos: Position) -> str:
        r, c = pos
        return chr(c + ord('a')) + str(8 - r)

    # ---------------- Helpers ---------------- #

    def in_bounds(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def is_white(self, p):
        return p.isupper()

    def is_black(self, p):
        return p.islower()

    def opponent(self):
        return "b" if self.turn == "w" else "w"

    # ---------------- Move Generation ---------------- #

    def generate_moves(self) -> List[Move]:
        moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and self.is_own_piece(piece):
                    moves.extend(self.generate_piece_moves(r, c, piece))

        # Filter illegal moves (king in check)
        legal = []
        for m in moves:
            if not self.leaves_king_in_check(m):
                legal.append(m)
        return legal

    def is_own_piece(self, piece):
        return (self.turn == "w" and self.is_white(piece)) or \
               (self.turn == "b" and self.is_black(piece))

    # ---------------- Piece Moves ---------------- #

    def generate_piece_moves(self, r, c, piece):
        piece = piece.lower()
        if piece == 'p':
            return self.pawn_moves(r, c)
        if piece == 'n':
            return self.knight_moves(r, c)
        if piece == 'b':
            return self.slider_moves(r, c, [(-1,-1), (-1,1), (1,-1), (1,1)])
        if piece == 'r':
            return self.slider_moves(r, c, [(-1,0), (1,0), (0,-1), (0,1)])
        if piece == 'q':
            return self.slider_moves(r, c, [(-1,-1), (-1,1), (1,-1), (1,1), (-1,0), (1,0), (0,-1), (0,1)])
        if piece == 'k':
            return self.king_moves(r, c)
        return []

    # ---------------- Pawn ---------------- #

    def pawn_moves(self, r, c):
        moves = []
        direction = -1 if self.turn == "w" else 1
        start_rank = 6 if self.turn == "w" else 1
        promotion_rank = 0 if self.turn == "w" else 7

        # Forward
        if self.in_bounds(r + direction, c) and self.board[r + direction][c] is None:
            if r + direction == promotion_rank:
                for p in ['q', 'r', 'b', 'n']:
                    moves.append(Move((r,c), (r+direction,c), promotion=p))
            else:
                moves.append(Move((r,c), (r+direction,c)))

            if r == start_rank and self.board[r + 2*direction][c] is None:
                moves.append(Move((r,c), (r+2*direction,c)))

        # Captures
        for dc in [-1, 1]:
            nr, nc = r + direction, c + dc
            if not self.in_bounds(nr, nc):
                continue

            target = self.board[nr][nc]
            if target and not self.is_own_piece(target):
                if nr == promotion_rank:
                    for p in ['q','r','b','n']:
                        moves.append(Move((r,c),(nr,nc),promotion=p))
                else:
                    moves.append(Move((r,c),(nr,nc)))

        # En passant
        if self.en_passant:
            if (r + direction, c - 1) == self.en_passant or \
               (r + direction, c + 1) == self.en_passant:
                moves.append(Move((r,c), self.en_passant, is_en_passant=True))

        return moves

    # ---------------- Knight ---------------- #

    def knight_moves(self, r, c):
        moves = []
        for dr, dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
            nr, nc = r + dr, c + dc
            if self.in_bounds(nr,nc):
                target = self.board[nr][nc]
                if target is None or not self.is_own_piece(target):
                    moves.append(Move((r,c),(nr,nc)))
        return moves

    # ---------------- Sliding Pieces ---------------- #

    def slider_moves(self, r, c, directions):
        moves = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while self.in_bounds(nr,nc):
                target = self.board[nr][nc]
                if target is None:
                    moves.append(Move((r,c),(nr,nc)))
                else:
                    if not self.is_own_piece(target):
                        moves.append(Move((r,c),(nr,nc)))
                    break
                nr += dr
                nc += dc
        return moves

    # ---------------- King ---------------- #

    def king_moves(self, r, c):
        moves = []
        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                if dr == dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if self.in_bounds(nr,nc):
                    target = self.board[nr][nc]
                    if target is None or not self.is_own_piece(target):
                        moves.append(Move((r,c),(nr,nc)))

        # Castling
        if self.turn == "w":
            if "K" in self.castling and self.can_castle_kingside():
                moves.append(Move((7,4),(7,6),is_castling=True))
            if "Q" in self.castling and self.can_castle_queenside():
                moves.append(Move((7,4),(7,2),is_castling=True))
        else:
            if "k" in self.castling and self.can_castle_kingside():
                moves.append(Move((0,4),(0,6),is_castling=True))
            if "q" in self.castling and self.can_castle_queenside():
                moves.append(Move((0,4),(0,2),is_castling=True))

        return moves

    # ---------------- Legality ---------------- #

    def leaves_king_in_check(self, move: Move) -> bool:
        board_copy = [row[:] for row in self.board]
        sr, sc = move.start
        er, ec = move.end
        piece = board_copy[sr][sc]

        board_copy[sr][sc] = None
        board_copy[er][ec] = piece

        return self.is_king_attacked(board_copy)

    def is_king_attacked(self, board):
        king = 'K' if self.turn == 'w' else 'k'
        for r in range(8):
            for c in range(8):
                if board[r][c] == king:
                    return self.square_attacked(board, r, c)
        return False

    def square_attacked(self, board, r, c):
        enemy_turn = self.opponent()
        saved_board = self.board
        saved_turn = self.turn
        self.board = board
        self.turn = enemy_turn

        for rr in range(8):
            for cc in range(8):
                piece = board[rr][cc]
                if piece and self.is_own_piece(piece):
                    for m in self.generate_piece_moves(rr,cc,piece):
                        if m.end == (r,c):
                            self.board = saved_board
                            self.turn = saved_turn
                            return True

        self.board = saved_board
        self.turn = saved_turn
        return False

    # ---------------- Castling Checks ---------------- #

    def can_castle_kingside(self):
        r = 7 if self.turn == "w" else 0
        return self.board[r][5] is None and self.board[r][6] is None

    def can_castle_queenside(self):
        r = 7 if self.turn == "w" else 0
        return self.board[r][1] is None and self.board[r][2] is None and self.board[r][3] is None


# ---------------- Example ---------------- #

if __name__ == "__main__":
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    gen = ChessMoveGenerator(fen)
    moves = gen.generate_moves()
    print(len(moves))
    for m in moves:
        print(m)
