import socket
import time
import uuid
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 8089))
usename = str(uuid.uuid4())
s.send(usename.encode())
# while True:
#     print("here")
#     s.send(str(time.time()).encode())
#     # incoming = s.recv(64)
#     # if len(incoming) > 0:
#     #     print(incoming.decode())
