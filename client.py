import socket
import time

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect(('localhost', 8089))
while True:
    clientsocket.send(str(time.time()).encode())
    time.sleep(1)
