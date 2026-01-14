# client.py
import zmq
import json
import time
import sys

client_id = sys.argv[1]

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

counter = 0

while True:
    request = {
        "client_id": client_id,
        "seq": counter,
        "value": counter
    }

    print(f"Client {client_id} sending: {request}")
    socket.send_string(json.dumps(request))

    reply = socket.recv_string()
    response = json.loads(reply)

    print(f"Client {client_id} received: {response}")

    counter += 1
