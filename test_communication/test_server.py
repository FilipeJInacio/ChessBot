# server.py
import zmq
import json
import time
import threading
import signal

# ----------------------
# Shared state
# ----------------------
shared_state = {
    "counter": 0,
    "value": 0.0,
    "last_update": time.time()
}

state_lock = threading.Lock()
running = True

# ----------------------
# Signal handling
# ----------------------
def shutdown(sig, frame):
    global running
    running = False

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

# ----------------------
# Publisher thread
# ----------------------
def publisher_thread(context):
    pub = context.socket(zmq.PUB)
    pub.setsockopt(zmq.SNDHWM, 1000)
    pub.bind("tcp://*:5556")

    # Allow subscribers to connect
    time.sleep(0.5)

    period = 1.0 / 15.0  # 15 FPS

    try:
        while running:
            with state_lock:
                message = shared_state.copy()

            pub.send_json(message)
            time.sleep(period)
    finally:
        pub.close()
        print("Publisher stopped")


# ----------------------
# Router thread
# ----------------------
def router_thread(context):
    router = context.socket(zmq.ROUTER)
    router.setsockopt(zmq.RCVHWM, 1000)
    router.setsockopt(zmq.SNDHWM, 1000)
    router.bind("tcp://*:5558")

    poller = zmq.Poller()
    poller.register(router, zmq.POLLIN)

    try:
        while running:
            events = dict(poller.poll(200))
            if router in events:
                identity, empty, payload = router.recv_multipart()
                request = json.loads(payload.decode())

                with state_lock:
                    # Modify shared JSON
                    shared_state["counter"] += 1
                    shared_state["value"] = request.get("value", shared_state["value"])
                    shared_state["last_update"] = time.time()

                    reply = {
                        "status": "ok",
                        "state": shared_state.copy()
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
# Main
# ----------------------
if __name__ == "__main__":
    context = zmq.Context.instance()

    pub_thread = threading.Thread(
        target=publisher_thread,
        args=(context,),
        daemon=True
    )

    router_thread = threading.Thread(
        target=router_thread,
        args=(context,),
        daemon=True
    )

    pub_thread.start()
    router_thread.start()

    # Wait for shutdown signal
    try:
        while running:
            time.sleep(0.5)
    finally:
        print("Server shutting down...")
        pub_thread.join()
        router_thread.join()
        context.term()
