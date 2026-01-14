from __future__ import annotations
from core.rules import RulesEngine
from core.state import classic_game_start

class Game:
    def __init__(self):
        self.state = classic_game_start()
        self.rules = RulesEngine()
        self.last_move = None
        self.history = []
        self.is_in_check = False # WHAT DO I DO WITH THIS?




