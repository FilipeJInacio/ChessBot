import zmq
import json

from game.game import Game
from core.move import Move

class Server:
    def __init__(self):
        self.game = Game()

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)
        self.socket.bind("tcp://127.0.0.1:5558")
        self.players = {} # identity → color
        self.turn_counter = 0
    

    def register_players(self):
        while len(self.players) < 2:
            identity, _, msg = self.socket.recv_multipart()
            data = json.loads(msg.decode("utf-8"))

            if data["type"] == "join":
                reply = {
                    "type": "join_ack",
                    "color": "white" if "white" not in self.players.values() else "black"
                }

                self.players[identity] = reply["color"]

                self.socket.send_multipart([identity, b"", json.dumps(reply).encode("utf-8")])


    def send_state(self, identity, legal_moves):
        payload = {
            "type": "state",
            "state": self.game.state.to_dict(),
            "legal_moves": [m.to_dict() for m in legal_moves]
        }

        self.socket.send_multipart([identity, b"", json.dumps(payload).encode("utf-8")])


    def receive_move(self, current_identity):
        while True:
            identity, _, msg = self.socket.recv_multipart()
            data = json.loads(msg.decode("utf-8"))
            if identity == current_identity and data["type"] == "move":
                return data


    def run(self):
        print("Waiting for players...")
        self.register_players()
        print("Players connected.")

        while True:
            print(f"Turn {self.turn_counter}: {self.game.state.turn}")
            self.turn_counter += 1

            # NOT WORKING
            legal_moves = self.game.rules.legal_moves(self.game.state)

            # find current player identity
            current_identity = next(i for i, c in self.players.items() if c == self.game.state.turn)

            self.send_state(current_identity, legal_moves)

            data = self.receive_move(current_identity)
            move = Move.from_dict(data["move"])
            print(f"Received move: {move}")
            if move not in legal_moves:
                raise RuntimeError("Illegal move")

            self.game.state = self.game.rules.apply_move(self.game.state, move)

            if self.game.rules.is_checkmate(self.game.state):
                print("Checkmate")
                break


if __name__ == "__main__":
    server = Server()
    server.run()
    print("Game over.")