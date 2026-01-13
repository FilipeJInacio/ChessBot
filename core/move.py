class Move:
    def __init__(self, piece, from_sq, to_sq, promotion=None):
        self.piece = piece
        self.from_sq = from_sq
        self.to_sq = to_sq
        self.promotion = promotion