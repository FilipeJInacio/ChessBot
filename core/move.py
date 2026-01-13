class Move:
    def __init__(self, from_sq, to_sq, promotion=None):
        self.from_sq = from_sq
        self.to_sq = to_sq
        self.promotion = promotion