import random
from game.game import Game
import time

if __name__ == "__main__":
    random.seed(42)
    game = Game()
    while True:
        print(game.state)
        legal_moves = game.rules.legal_moves(game.state)
        if not legal_moves:
            print("No legal moves available. Game over.")
            break
        move = random.choice(legal_moves)
        game.state = game.rules.apply_move(game.state, move)
        time.sleep(1)  # Pause for a second to observe the game progression