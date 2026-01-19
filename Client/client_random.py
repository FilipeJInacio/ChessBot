import zmq
import random
import uuid
import signal
from game import ChessGame

class Client_random:
    def __init__(self):
        self.game = ChessGame()

        self.context = zmq.Context()
        self.dealer = self.context.socket(zmq.DEALER)
        client_id = uuid.uuid4().bytes
        self.dealer.setsockopt(zmq.IDENTITY, client_id)
        self.dealer.setsockopt(zmq.RCVTIMEO, 200)
        self.dealer.setsockopt(zmq.LINGER, 0)
        self.dealer.connect("tcp://localhost:5557")

        self.running = True
        # Signal handling
        signal.signal(signal.SIGINT, self._shutdown_signal)
        signal.signal(signal.SIGTERM, self._shutdown_signal)

    def _shutdown_signal(self, sig, frame):
        print("Shutdown signal received")
        self.running = False

    def run(self):
        state = "joining"

        # send join request
        self.dealer.send_multipart([b"join", b""])

        # wait for join ack
        while self.running:
            try:
                msg = self.dealer.recv_multipart()
            except zmq.Again:
                continue  

            msg_type = msg[0]
            payload = msg[1] if len(msg) > 1 else b""

            if msg_type == b"server_shutdown":
                print("Server is shutting down")
                self.running = False
                continue

            if msg_type == b"game_over":
                winner = payload.decode("utf-8") if payload else "Draw"
                print(f"Game over! Winner: {winner}")
                self.running = False
                continue

            # STATE 2
            if state == "playing":
                if msg_type == b"your_turn":
                    # what was the last move?
                    last_move_uci = payload.decode("utf-8") if payload else None

                    if last_move_uci:
                        self.game.make_move(last_move_uci)

                    legal_moves = self.game.get_possible_moves()

                    move_uci = random.choice(legal_moves)

                    self.game.make_move(move_uci)

                    self.dealer.send_multipart([b"move", move_uci.encode("utf-8")])

                    state = "waiting_for_move_ack"
                continue

            # STATE 3
            if state == "waiting_for_move_ack":
                if msg_type == b"move_ack":
                    state = "playing"
                elif msg_type == b"move_nack":
                    raise RuntimeError("Move was rejected by server")
                continue

            # STATE 1
            if state == "joining":
                if msg_type == b"join_ack":
                    print("Joined game")
                    self.color = payload.decode("utf-8")
                    self.game.reset()
                    state = "playing"
                elif msg_type == b"join_nack":
                    print("Join request denied")
                    return
                
            

        self.dealer.close()
        self.context.term()























