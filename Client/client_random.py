import random
from Client.client import Client

class Client_random(Client):
    def select_move(self):
        legal_moves = self.game.get_possible_moves()
        return random.choice(legal_moves)























