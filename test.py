import random
from game.game import Game
import time

if __name__ == "__main__":
    random.seed(42)
    game = Game()

    legal_moves = game.rules.legal_moves(game.state)
    print(len(legal_moves))
    group_legal_moves = []
    for each in legal_moves:
        game.state = game.rules.apply_move(game.state, each)
        group_legal_moves.extend(game.rules.legal_moves(game.state))
    legal_moves = group_legal_moves
    print(len(legal_moves))
    group_legal_moves = []
    for each in legal_moves:
        game.state = game.rules.apply_move(game.state, each)
        group_legal_moves.extend(game.rules.legal_moves(game.state))
    legal_moves = group_legal_moves
    print(len(legal_moves))