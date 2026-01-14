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
        self.router_port = 5558 # For move requests
        self.fps = 1 # UI update rate

        # Threads
        self.pub_thread = threading.Thread(target=self._publisher, daemon=True)
        self.router_thread = threading.Thread(target=self._router, daemon=True)

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

    def _router(self):
        socket = self.context.socket(zmq.ROUTER)
        socket.setsockopt(zmq.SNDHWM, 1000)
        socket.setsockopt(zmq.RCVHWM, 1000)
        socket.setsockopt(zmq.RCVTIMEO, 200)
        socket.bind(f"tcp://*:{self.router_port}")

        # Passive player registration
        while self.running:
            try:
                identity, _, payload = socket.recv_multipart()
                msg = json.loads(payload.decode())

                if len(self.players) < 2:
                    if msg["type"] == "join":
                        color = "white" if "white" not in self.players.values() else "black"
                        self.players[identity] = color
                    else:
                        raise RuntimeError("Unexpected message before game start")
                
                if len(self.players) == 2:
                    break
                    
            except zmq.Again:
                pass

        if not self.running:
            socket.close()
            print("Router stopped before game start")
            return

        # Active player messaging
        while self.running:
            try:
                identity = next(i for i, c in self.players.items() if c == self.game.state.turn)
                time.sleep(3)

                with self.state_lock:
                    legal_moves = self.game.rules.legal_moves(self.game.state)
                moves_list = [m.to_dict() for m in legal_moves]
                reply = {"type": "moves", "moves": moves_list}
                socket.send_multipart([identity,b"",json.dumps(reply).encode()])
                

                identity_recv, _, payload = socket.recv_multipart()
                if identity_recv != identity:
                    raise RuntimeError("Received message from unexpected identity")
                msg = json.loads(payload.decode())
                if msg["type"] == "moves":
                    move_dict = msg["moves"][0]
                    move = Move.from_dict(move_dict)
                    with self.state_lock:
                        if move in legal_moves:
                            self.game.state = self.game.rules.apply_move(self.game.state, move)
                        else:
                            raise RuntimeError("Illegal move received")
                    
            except zmq.Again:
                if not self.running:
                    break

        # send closing message to all players
        for identity in self.players.keys():
            try:
                socket.send_multipart([identity,b"",json.dumps({"type":"close"}).encode()])
                print(f"Sent close signal to player {identity}, color {self.players[identity]}")
            except zmq.Again:
                pass


        socket.close()
        return








    def start(self):
        print("Starting server...")
        self.pub_thread.start()
        self.router_thread.start()

        try:
            while self.running:
                time.sleep(1)
        finally:
            print("Server shutting down...")
            self.pub_thread.join()
            self.router_thread.join()
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