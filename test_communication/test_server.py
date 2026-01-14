import zmq
import threading
import json
import time
import signal

class PubRouterServer:
    def __init__(self, pub_port=5556, router_port=5558, fps=15):
        self.pub_port = pub_port
        self.router_port = router_port
        self.fps = fps

        self.context = zmq.Context.instance()

        # Shared state
        self.state = {
            "counter": 0,
            "value": 0.0,
            "last_update": time.time()
        }
        self.state_lock = threading.Lock()
        self.running = True

        # Threads
        self.pub_thread = threading.Thread(target=self._publisher, daemon=True)
        self.router_thread = threading.Thread(target=self._router, daemon=True)

        # Signal handling
        signal.signal(signal.SIGINT, self._shutdown_signal)
        signal.signal(signal.SIGTERM, self._shutdown_signal)

    # ----------------------
    # Internal methods
    # ----------------------
    def _shutdown_signal(self, sig, frame):
        print("Shutdown signal received")
        self.running = False

    def _publisher(self):
        pub = self.context.socket(zmq.PUB)
        pub.setsockopt(zmq.SNDHWM, 1000)
        pub.setsockopt(zmq.LINGER, 0)
        pub.bind(f"tcp://*:{self.pub_port}")

        # Allow subscribers to connect
        time.sleep(0.5)
        period = 1.0 / self.fps

        try:
            while self.running:
                with self.state_lock:
                    message = self.state.copy()
                pub.send_json(message)
                time.sleep(period)
        finally:
            pub.close()
            print("Publisher stopped")

    def _router(self):
        router = self.context.socket(zmq.ROUTER)
        router.setsockopt(zmq.SNDHWM, 1000)
        router.setsockopt(zmq.RCVHWM, 1000)
        router.setsockopt(zmq.LINGER, 0)
        router.bind(f"tcp://*:{self.router_port}")

        poller = zmq.Poller()
        poller.register(router, zmq.POLLIN)

        try:
            while self.running:
                events = dict(poller.poll(200))
                if router in events:
                    try:
                        identity, empty, payload = router.recv_multipart()
                        request = json.loads(payload.decode())
                    except Exception as e:
                        print("Failed to decode request:", e)
                        continue

                    with self.state_lock:
                        # Update shared state
                        self.state["counter"] += 1
                        self.state["value"] = request.get("value", self.state["value"])
                        self.state["last_update"] = time.time()
                        reply = {
                            "status": "ok",
                            "state": self.state.copy()
                        }

                    router.send_multipart([
                        identity,
                        b"",
                        json.dumps(reply).encode()
                    ])
        finally:
            router.close()
            print("Router stopped")

    # ----------------------
    # Public API
    # ----------------------
    def start(self):
        print("Starting server...")
        self.pub_thread.start()
        self.router_thread.start()

        try:
            while self.running:
                time.sleep(0.5)
        finally:
            print("Server shutting down...")
            self.pub_thread.join()
            self.router_thread.join()
            self.context.term()
            print("Server terminated")

if __name__ == "__main__":
    server = PubRouterServer(pub_port=5556, router_port=5558, fps=15)
    server.start()
