# server.py
import zmq
import json
import time

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

print("REP server started")

while True:
    message = socket.recv_string()
    data = json.loads(message)

    print(f"Received from client {data['client_id']}: {data['value']}")

    # Simulate work
    time.sleep(0.1)

    response = {
        "client_id": data["client_id"],
        "status": "ok",
        "result": data["value"] * 2
    }

    socket.send_string(json.dumps(response))
