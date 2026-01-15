# 8 | 56 57 58 59 60 61 62 63
# 7 | 48 49 50 51 52 53 54 55
# 6 | 40 41 42 43 44 45 46 47
# 5 | 32 33 34 35 36 37 38 39
# 4 | 24 25 26 27 28 29 30 31
# 3 | 16 17 18 19 20 21 22 23
# 2 |  8  9 10 11 12 13 14 15
# 1 |  0  1  2  3  4  5  6  7
#      a  b  c  d  e  f  g  h


WHITE, BLACK = 0, 1
PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING = range(6)

def bit(square: int) -> int:
    return 1 << square

class Board:
    def __init__(self):
        # Number of pieces of each type for each color
        self.pieces = {WHITE: {PAWN: 0, KNIGHT: 0, BISHOP: 0, ROOK: 0, QUEEN: 0, KING: 0}, BLACK: {PAWN: 0, KNIGHT: 0, BISHOP: 0, ROOK: 0, QUEEN: 0, KING: 0}}
        self.side_to_move = WHITE

    # ------------------------------------------------
    # Occupancy helpers
    # ------------------------------------------------

    def occupied(self) -> int:
        """All occupied squares."""
        return self.occupied_color(WHITE) | self.occupied_color(BLACK)

    def occupied_color(self, color: int) -> int:
        """Occupied squares for one color."""
        occ = 0
        for piece in self.pieces[color].values():
            occ |= piece
        return occ

    def empty(self, square: int) -> bool:
        return not (self.occupied() & bit(square))

    # ------------------------------------------------
    # Piece queries
    # ------------------------------------------------

    def what_is(self, square: int):
        """
        Returns (color, piece_type) or None.
        """
        mask = bit(square)
        for color in (WHITE, BLACK):
            for piece_type, bb in self.pieces[color].items():
                if bb & mask:
                    return color, piece_type
        return None

    def has_piece(self, square: int) -> bool:
        return bool(self.occupied() & bit(square))

    # ------------------------------------------------
    # Piece mutation
    # ------------------------------------------------

    def put_piece(self, color: int, piece_type: int, square: int):
        """
        Place a piece on the board.
        Assumes the square is empty.
        """
        assert not self.has_piece(square), f"Square {square} is not empty"
        self.pieces[color][piece_type] |= bit(square)

    def remove_piece(self, square: int):
        """
        Remove any piece from the square.
        """
        mask = bit(square)
        for color in (WHITE, BLACK):
            for piece_type in self.pieces[color]:
                if self.pieces[color][piece_type] & mask:
                    self.pieces[color][piece_type] &= ~mask
                    return
        raise ValueError(f"No piece on square {square}")

    def move_piece(self, from_sq: int, to_sq: int):
        """
        Move a piece from one square to another.
        Captures any piece on the destination square.
        """
        piece = self.what_is(from_sq)
        if piece is None:
            raise ValueError("No piece to move")

        color, piece_type = piece

        if self.has_piece(to_sq):
            self.remove_piece(to_sq)

        self.remove_piece(from_sq)
        self.put_piece(color, piece_type, to_sq)

    # ------------------------------------------------
    # Debug helpers
    # ------------------------------------------------

    def print_board(self):
        symbols = {
            (WHITE, PAWN):   "P",
            (WHITE, KNIGHT): "N",
            (WHITE, BISHOP): "B",
            (WHITE, ROOK):   "R",
            (WHITE, QUEEN):  "Q",
            (WHITE, KING):   "K",
            (BLACK, PAWN):   "p",
            (BLACK, KNIGHT): "n",
            (BLACK, BISHOP): "b",
            (BLACK, ROOK):   "r",
            (BLACK, QUEEN):  "q",
            (BLACK, KING):   "k",
        }

        for rank in reversed(range(8)):
            row = []
            for file in range(8):
                sq = rank * 8 + file
                piece = self.what_is(sq)
                if piece:
                    row.append(symbols[piece])
                else:
                    row.append(".")
            print(" ".join(row))
        print()




def initial_board() -> Board:
    b = Board()

    # White pieces
    for file in range(8):
        b.put_piece(WHITE, PAWN, 8 + file)

    b.put_piece(WHITE, ROOK, 0)
    b.put_piece(WHITE, KNIGHT, 1)
    b.put_piece(WHITE, BISHOP, 2)
    b.put_piece(WHITE, QUEEN, 3)
    b.put_piece(WHITE, KING, 4)
    b.put_piece(WHITE, BISHOP, 5)
    b.put_piece(WHITE, KNIGHT, 6)
    b.put_piece(WHITE, ROOK, 7)

    # Black pieces
    for file in range(8):
        b.put_piece(BLACK, PAWN, 48 + file)

    b.put_piece(BLACK, ROOK, 56)
    b.put_piece(BLACK, KNIGHT, 57)
    b.put_piece(BLACK, BISHOP, 58)
    b.put_piece(BLACK, QUEEN, 59)
    b.put_piece(BLACK, KING, 60)
    b.put_piece(BLACK, BISHOP, 61)
    b.put_piece(BLACK, KNIGHT, 62)
    b.put_piece(BLACK, ROOK, 63)

    return b



if __name__ == "__main__":
    board = initial_board()
    board.print_board()

    print("Moving pawn e2 → e4")
    board.move_piece(12, 28)
    board.print_board()
