import zmq
import time
import signal

class Client:
    def __init__(self):
        self.context = zmq.Context()
        self.sub = self.context.socket(zmq.SUB)
        self.sub.connect("tcp://localhost:5556")
        self.sub.setsockopt_string(zmq.SUBSCRIBE, "")
        self.sub.setsockopt(zmq.RCVTIMEO, 500)  # non-blocking recv every 0.5 s

        self.running = True
        self.HEARTBEAT_TIMEOUT = 2.0  # seconds
        # Signal handling
        signal.signal(signal.SIGINT, self._shutdown_signal)
        signal.signal(signal.SIGTERM, self._shutdown_signal)

    def _shutdown_signal(self, sig, frame):
        print("Shutdown signal received")
        self.running = False

    def run(self):
        last_msg_time = time.time()

        try:
            while self.running:
                try:
                    msg = self.sub.recv_json()
                    state = GameState.from_dict(msg)
                    print(state)
                    last_msg_time = time.time()
                except zmq.Again:
                    # Timeout: check if server is alive
                    if time.time() - last_msg_time > self.HEARTBEAT_TIMEOUT:
                        print("Timeout")
                        break
        finally:
            self.sub.close()
            self.context.term()
            print("SUB client terminated")




if __name__ == "__main__":
    player = Client()
    player.run()
    print("Stream over.")