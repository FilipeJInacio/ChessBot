import zmq
import json
import random
import uuid
import pygame as p

from render.board_image import BoardRenderer

class Client:
    def __init__(self):
        self.render = BoardRenderer()

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
    

    def run(self):
        p.init()
        self.render.screen = p.display.set_mode((self.render.WIDTH, self.render.HEIGHT))
        p.display.set_caption('Chess')
        clock = p.time.Clock()
        self.render.screen.fill(p.Color("white"))
        self.render.load_images()

        running = True
        while running:
            for e in p.event.get():
                if e.type == p.QUIT:
                    running = False

            _, msg = self.socket.recv_multipart()
            msg = json.loads(msg.decode("utf-8"))

            if msg["type"] != "state":
                continue

            state = msg["state"]
            legal_moves = msg["legal_moves"]

            self.render.render(state)
            clock.tick(self.render.MAX_FPS)
            p.display.flip()

            move = self.choose_move(state, legal_moves)

            self.socket.send_multipart([b"",json.dumps({"type": "move","move": move}).encode("utf-8")])



if __name__ == "__main__":
    player = Client()
    player.run()
    print("Game over.")