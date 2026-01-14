import time
import zmq
import json
import time
import threading
import signal
from game.game import Game
from core.move import Move



class Server:
    def __init__(self):
        self.game = Game() # Everything game-related
        self.turn_counter = 0 # To track turns
        self.players = {} # identity -> color mapping

        self.context = zmq.Context.instance() # For communication of the 2 threads
        self.state_lock = threading.Lock() # To protect shared state
        self.running = True # For shutdown
        self.pub_port = 5556 # For state updates
        self.response_port = 5558 # For move requests
        self.fps = 1 # UI update rate

        # Threads
        self.pub_thread = threading.Thread(target=self._publisher, daemon=True)
        self.rep_thread = threading.Thread(target=self._response, daemon=True)

        # Signal handling
        signal.signal(signal.SIGINT, self._shutdown_signal)
        signal.signal(signal.SIGTERM, self._shutdown_signal)

    def _shutdown_signal(self, sig, frame):
        print("Shutdown signal received")
        self.running = False

    def _publisher(self):
        pub = self.context.socket(zmq.PUB)
        pub.setsockopt(zmq.SNDHWM, 1000)
        pub.bind(f"tcp://*:{self.pub_port}")

        period = 1.0 / self.fps

        try:
            while self.running:
                with self.state_lock:
                    message = self.game.state.to_dict()
                pub.send_json(message)
                time.sleep(period)
        finally:
            pub.close()
            print("Publisher stopped")

    def _response(self):
        response = self.context.socket(zmq.REP)
        response.setsockopt(zmq.SNDHWM, 1000)
        response.setsockopt(zmq.RCVHWM, 1000)
        response.setsockopt(zmq.RCVTIMEO, 500) # Timeout to verify if still running
        #response.setsockopt(zmq.SNDTIMEO, 500) # It is expected that clients always recv
        response.setsockopt(zmq.LINGER, 0)
        response.bind(f"tcp://*:{self.response_port}")

        while len(self.players) < 2:
            try:
                identity, _, msg = response.recv_multipart()
                data = json.loads(msg.decode("utf-8"))

                if data["type"] == "join":
                    reply = {
                        "type": "join_ack",
                        "color": "white" if "white" not in self.players.values() else "black"
                    }

                    self.players[identity] = reply["color"]

                    response.send_multipart([identity, b"", json.dumps(reply).encode("utf-8")])
            except zmq.Again:
                if not self.running:
                    response.close()
                    print("Response socket stopped")
                    break


        try:
            while self.running:
                identity, _, msg = response.recv_multipart()
                request = json.loads(msg.decode("utf-8"))

                # is it a recognized identity?
                if identity not in self.players:
                    reply = {"status": "error", "message": "unrecognized identity"}
                    response.send_multipart([identity, b"", json.dumps(reply).encode("utf-8")])
                    continue

                print(request) # To do

                response.send_multipart([identity, b"", json.dumps(reply).encode("utf-8")])
        finally:
            response.close()
            print("Response socket stopped")

    def start(self):
        print("Starting server...")
        self.pub_thread.start()
        self.rep_thread.start()

        try:
            while self.running:
                time.sleep(1)
        finally:
            print("Server shutting down...")
            self.pub_thread.join()
            self.rep_thread.join()
            self.context.term()
            print("Server terminated")

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

        while running:
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

            time.sleep(1)

if __name__ == "__main__":
    server = Server()
    server.start()