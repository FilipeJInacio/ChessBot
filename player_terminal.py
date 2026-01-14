import zmq
import random
import uuid
import json
import signal
from core.state import GameState

class Client:
    def __init__(self):
        self.context = zmq.Context()
        self.req = self.context.socket(zmq.REQ)
        client_id = uuid.uuid4().bytes
        self.req.setsockopt(zmq.IDENTITY, client_id)
        self.req.setsockopt(zmq.RCVTIMEO, 2000)
        self.req.setsockopt(zmq.LINGER, 0)
        self.req.connect("tcp://localhost:5558")

        self.running = True
        # Signal handling
        signal.signal(signal.SIGINT, self._shutdown_signal)
        signal.signal(signal.SIGTERM, self._shutdown_signal)

    def _shutdown_signal(self, sig, frame):
        print("Shutdown signal received")
        self.running = False

    def run(self):

        request = {"type": "join"}
        self.req.send_json(request)

        while self.running:
            try:
                msg = self.req.recv_json()
            except zmq.Again:
                continue  


            if msg["type"] == "moves":
                answer = {"type": "moves", "moves": [random.choice(msg["moves"])]}  
                self.req.send_json(answer)
            elif msg["type"] == "close":
                break   
            else:
                raise RuntimeError("Unexpected message type")

        self.req.close()
        self.context.term()





if __name__ == "__main__":
    player = Client()
    player.run()
    print("Stream over.")
    exit(0) # cause i suck with ZMQ cleanup





















import zmq
import json
import random
import uuid

from core.state import GameState

class Client:
    def __init__(self):
        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(zmq.DEALER)
        client_id = uuid.uuid4().bytes
        self.socket.setsockopt(zmq.IDENTITY, client_id)
        self.socket.connect("tcp://localhost:5558")

        request = {"type": "join"}
        self.socket.send_multipart([b"",json.dumps(request).encode("utf-8")])

        _, msg = self.socket.recv_multipart()

        reply = json.loads(msg.decode("utf-8"))
        
        if reply["type"] != "join_ack":
            raise RuntimeError("Failed to join game")

        self.color = reply["color"]
        print("Joined game as", self.color)

    def choose_move(self, state, legal_moves):
        return random.choice(legal_moves) 
    
    def display_state(self, state: GameState):
        print(state)

    def run(self):

        running = True
        while running:
            _, msg = self.socket.recv_multipart()
            msg = json.loads(msg.decode("utf-8"))

            if msg["type"] != "state":
                continue

            state = msg["state"]
            legal_moves = msg["legal_moves"]

            self.display_state(GameState.from_dict(state))

            move = self.choose_move(state, legal_moves)

            self.socket.send_multipart([b"",json.dumps({"type": "move","move": move}).encode("utf-8")])



if __name__ == "__main__":
    player = Client()
    player.run()
    print("Game over.")