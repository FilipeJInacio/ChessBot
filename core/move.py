class Move:
    def __init__(self, from_sq, to_sq, promotion=None, en_passant=False, castling=False):
        self.from_sq = from_sq
        self.to_sq = to_sq
        self.promotion = promotion
        self.en_passant = en_passant
        self.castling = castling

    def to_dict(self):
        return {
            "from": self.from_sq,
            "to": self.to_sq,
            "promotion": self.promotion,
            "en_passant": self.en_passant,
            "castling": self.castling
        }

    @staticmethod
    def from_dict(d):
        return Move(d["from"], d["to"], d["promotion"], d["en_passant"], d["castling"])
    
    def __repr__(self):
        return f"Move({self.from_sq} -> {self.to_sq}, promotion={self.promotion}, en_passant={self.en_passant}, castling={self.castling})"