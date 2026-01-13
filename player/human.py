from player.base import Player
from core.state import GameState
from core.move import Move

class HumanPlayer(Player):
    def __init__(self, input_handler):
        self.input_handler = input_handler

    def choose_move(self, state: GameState, legal_moves: list[Move]) -> Move:
        return self.input_handler.get_move(state, legal_moves)