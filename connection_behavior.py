import json
import socket


def send_json(x):
    return json.dumps(x).encode()


def read_json(x):
    return json.loads(x.decode())


def wait_for_message(socket: socket.socket):
    # todo,timeout?
    incoming = None
    while incoming is None:
        incoming = socket.recv(1024)
        if len(incoming) > 0:
            response = read_json(incoming)
            return response
        else:
            incoming = None
