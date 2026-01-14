# req_client.py
import zmq
import json
import time
import signal
import sys

running = True
REQ_TIMEOUT = 2000  # milliseconds

def shutdown(sig, frame):
    global running
    running = False

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

context = zmq.Context()
req = context.socket(zmq.REQ)
req.connect("tcp://localhost:5558")
req.setsockopt(zmq.RCVTIMEO, REQ_TIMEOUT)
req.setsockopt(zmq.SNDTIMEO, REQ_TIMEOUT)
req.setsockopt(zmq.LINGER, 0)


try:
    while running:
        request = {"value": 42}  # example payload
        try:
            req.send_json(request)
        except zmq.Again:
            print("Could not send request, server might be down")
            break

        try:
            reply = req.recv_json()
            print("REQ received:", reply)
        except zmq.Again:
            print("No reply from server, shutting down")
            break

        time.sleep(2)
finally:
    req.close()
    context.term()
    print("REQ client terminated")
