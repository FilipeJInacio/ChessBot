import zmq
import signal
from game import ChessGame

class UI_terminal:
    def __init__(self):
        self.game = ChessGame()

        self.context = zmq.Context()
        self.sub = self.context.socket(zmq.SUB)
        self.sub.connect("tcp://localhost:5556")
        self.sub.setsockopt_string(zmq.SUBSCRIBE, "")
        self.sub.setsockopt(zmq.RCVTIMEO, 200)  # exit if no message in 2s

        self.running = True

        # Signal handling
        signal.signal(signal.SIGINT, self._shutdown_signal)
        signal.signal(signal.SIGTERM, self._shutdown_signal)

    def _shutdown_signal(self, sig, frame):
        print("Shutdown signal received")
        self.running = False

    def run(self):
        last_msg = b""
        while self.running:
            try:
                msg = self.sub.recv()
                if msg != last_msg:
                    self.game.from_fen(msg.decode("utf-8"))
                    last_msg = msg
                self.game.print_board()
            except zmq.Again:
                self.running = False
                print("Timeout: No message received")

        self.sub.close()
        self.context.term()
        print("SUB client terminated")




if __name__ == "__main__":
    ui = UI_terminal()
    ui.run()