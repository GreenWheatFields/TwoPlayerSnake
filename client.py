import socket
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 8089))
while True:
    s.send(str(time.time()).encode())
    incoming = s.recv(64)
    if len(incoming) > 0:
        print(incoming.decode())
