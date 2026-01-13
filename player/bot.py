from player.base import Player
import random
from core.state import GameState
from core.move import Move


class BotPlayer(Player):
    def choose_move(self, state: GameState, legal_moves: list[Move]) -> Move:
        return random.choice(legal_moves)