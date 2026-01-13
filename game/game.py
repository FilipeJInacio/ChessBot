from __future__ import annotations
from core.rules import RulesEngine
from core.state import classic_game_start

class Game:
    def __init__(self, player_white, player_black):
        self.state = classic_game_start()
        self.players = {
            "white": player_white,
            "black": player_black
        }
        self.rules = RulesEngine()

    def run(self):
        while True:
            player = self.players[self.state.turn]
            legal_moves = self.rules.legal_moves(self.state)

            move = player.choose_move(self.state, legal_moves)
            self.state = self.rules.apply_move(self.state, move)

            if self.rules.is_checkmate(self.state):
                break