class Board:
    def __init__(self):
        self.grid = [[None]*8 for _ in range(8)]

    def piece_at_classical_setup(self):
        self.grid[0] = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
        self.grid[1] = ['p']*8
        self.grid[6] = ['P']*8
        self.grid[7] = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']

    def board_from_fen(self, fen: str):
        ...

    def move_piece(self, move):
        ...