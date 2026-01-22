import time
import zmq
import time
import threading
import signal
from game import ChessGame
import chess


class Server:
    def __init__(self):
        self.game = ChessGame() # Everything game-related
        self.turn_counter = 0 # To track turns
        self.players = {} # color mapping -> identity

        self.context = zmq.Context.instance() # For communication of the 2 threads
        self.running = True # For shutdown
        self.pub_port = 5556 # For state updates
        self.router_port = 5557 # For move requests
        self.fps = 15 # UI update rate

        # Threads
        self.pub_thread = threading.Thread(target=self._publisher, daemon=True)
        self.router_thread = threading.Thread(target=self._router, daemon=True)
        self.state_lock = threading.Lock() # To protect shared state

        # Signal handling
        signal.signal(signal.SIGINT, self._shutdown_signal)
        signal.signal(signal.SIGTERM, self._shutdown_signal)

    def _shutdown_signal(self, sig, frame):
        print("Shutdown signal received")
        self.running = False

    def _publisher(self):
        pub = self.context.socket(zmq.PUB)
        pub.bind(f"tcp://*:{self.pub_port}")

        period = 1.0 / self.fps

        try:
            while self.running:
                with self.state_lock:
                    message = {"fen": self.game.get_board_fen(), "last_move": self.game.get_last_move().uci() if self.game.get_last_move() else None}
                pub.send_json(message)
                time.sleep(period)
        finally:
            pub.close()
            print("Publisher stopped")

    def _router(self):
        state = "waiting_for_players"
        socket = self.context.socket(zmq.ROUTER)
        socket.setsockopt(zmq.RCVTIMEO, 200)
        socket.bind(f"tcp://*:{self.router_port}")

        while self.running:
            try:
                time.sleep(0.3)
                msg = socket.recv_multipart()
                identity = msg[0]
                msg_type = msg[1]
                payload = msg[2] if len(msg) > 2 else b""
            except zmq.Again:
                continue

            # STATE 1   
            if state == "waiting_for_players":
                if msg_type == b"join":
                    if len(self.players) == 2:
                        socket.send_multipart([identity, b"join_nack", b""])
                        continue

                    color = "White" if "White" not in self.players else "Black"
                    self.players[color] = identity
                    print(f"Player joined as {color}")
                    socket.send_multipart([identity, b"join_ack", color.encode()])

                    if len(self.players) == 2:
                        self.game.reset()
                        print("Game started")
                        state = "active_game"
                else:
                    print("Unexpected Message")


            # STATE 3
            if state == "waiting_for_move":
                if msg_type == b"move":
                    if identity != current_player_identity:
                        continue

                    move = chess.Move.from_uci(payload.decode("utf-8"))
                    if move in legal_moves:
                        with self.state_lock:
                            self.game.make_move(move)
                        socket.send_multipart([identity, b"move_ack", b""])
                        state = "active_game"
                    else:
                        socket.send_multipart([identity, b"move_nack", b""])
                else:
                    print("Unexpected Message")
                    continue

            # STATE 2
            if state == "active_game":
                if self.game.is_game_over():
                    print(f"Game over detected by {self.game.game_over_reason()}")
                    winner = self.game.get_winner()
                    if winner == chess.WHITE:
                        winner = "White"
                    elif winner == chess.BLACK:
                        winner = "Black"
                    elif winner is None:
                        winner = "Draw"
                    for color, identity in self.players.items():
                        socket.send_multipart([identity, b"game_over", winner.encode("utf-8")])
                    state = "waiting_for_players"
                    self.turn_counter = 0
                    self.players = {}
                    print("Game over announced, waiting for new players")
                    continue
                self.turn_counter += 1
                current_player_identity = self.players[self.game.turn()]
                last_move = self.game.get_last_move()
                socket.send_multipart([current_player_identity, b"your_turn", last_move.uci().encode("utf-8") if last_move else b""])

                legal_moves = self.game.get_possible_moves()
                state = "waiting_for_move"
                continue


        # Send shutdown to all clients
        for color, identity in self.players.items():
            socket.send_multipart([identity, b"server_shutdown", b""])

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



if __name__ == "__main__":
    server = Server()
    server.start()