import pygame as p
import zmq
import time
import signal
from core.state import GameState
from core.move import Move
from render.board_image import BoardRenderer

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

        self.render = BoardRenderer()

    def _shutdown_signal(self, sig, frame):
        print("Shutdown signal received")
        self.running = False

    def run(self):
        p.init()
        self.render.screen = p.display.set_mode((self.render.WIDTH, self.render.HEIGHT))
        p.display.set_caption('Chess')
        clock = p.time.Clock()
        self.render.screen.fill(p.Color("white"))
        self.render.load_images()
        last_msg_time = time.time()

        try:
            while self.running:
                for e in p.event.get():
                    if e.type == p.QUIT:
                        self.running = False
                try:
                    msg = self.sub.recv_json()
                    state = GameState.from_dict(msg["state"])
                    last_move = Move.from_dict(msg["last_move"]) if msg["last_move"] else None
                    is_in_check = msg.get("is_in_check")
                    self.render.render(state, last_move, is_in_check)
                    clock.tick(self.render.MAX_FPS)
                    p.display.flip()
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