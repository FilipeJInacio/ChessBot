# sub_client.py
import zmq
import signal
import time
import sys

running = True
HEARTBEAT_TIMEOUT = 2.0  # seconds

def shutdown(sig, frame):
    global running
    running = False

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

context = zmq.Context()
sub = context.socket(zmq.SUB)
sub.connect("tcp://localhost:5556")
sub.setsockopt_string(zmq.SUBSCRIBE, "")
sub.setsockopt(zmq.RCVTIMEO, 500)  # non-blocking recv every 0.5 s

last_msg_time = time.time()

try:
    while running:
        try:
            msg = sub.recv_json()
            print("SUB received:", msg)
            last_msg_time = time.time()
        except zmq.Again:
            # Timeout: check if server is alive
            if time.time() - last_msg_time > HEARTBEAT_TIMEOUT:
                print("No telemetry from server, shutting down")
                break
finally:
    sub.close()
    context.term()
    print("SUB client terminated")
