import chess
import zmq
import uuid
import signal
from game import ChessGame

class Client:
    def __init__(self):
        self.game = ChessGame()

        self.total_time = 0

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

    def select_move(self):
        raise NotImplementedError("select_move must be implemented by subclasses")

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
                print(f"Game over! Winner: {winner}. Total time: {self.total_time:.2f} seconds")
                self.running = False
                continue

            # STATE 2
            if state == "playing":
                if msg_type == b"your_turn":
                    # what was the last move?
                    last_move_uci = payload.decode("utf-8") if payload else None

                    if last_move_uci:
                        self.game.make_move(chess.Move.from_uci(last_move_uci))

                    move, time = self.select_move()
                    self.total_time += time

                    self.game.make_move(move)

                    self.dealer.send_multipart([b"move", move.uci().encode("utf-8")])

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























