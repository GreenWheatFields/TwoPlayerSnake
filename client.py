import socket
import time
import uuid
import json

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 8089))
usename = str(uuid.uuid4())
s.send(usename.encode())
while True:
    incoming = s.recv(128)
    print(incoming.decode())
    print(json.loads(incoming))
    break


#todo, small window that shows while attempting to connect. automatically closes when client receives instruction to build window


# while True:
#     print("here")
#     s.send(str(time.time()).encode())
#     # incoming = s.recv(64)
#     # if len(incoming) > 0:
#     #     print(incoming.decode())
