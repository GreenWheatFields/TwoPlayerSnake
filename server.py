import socket
import time
import json
import random

width = 500
height = 500
white = (255, 255, 255)


class Server:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 8089))
        self.server_socket.listen(2)
        self.conn, self.address = self.server_socket.accept()
        self.game_over = False
        self.initialized = False
        self.players = {}
        self.initializeGame()

    def hostGame(self):

        pass

    def initializeGame(self):
        while len(self.players) < 2:
            incoming = self.conn.recv(64)
            if len(incoming) > 0:
                if incoming.decode() not in self.players:
                    self.players[incoming.decode()] = self.address[0]
                    response = {"INSTRUCTION": "WAIT",
                                "WIDTH": width,
                                "HEIGHT": height,
                                "WAITING": False if len(self.players) >= 2 else True}
                    response = json.dumps(response)
                    self.conn.sendall(response.encode())
                else:
                    # client querying server before intialized
                    pass
        temp = [self.players.keys()]
        random.shuffle(temp)
        response = {"INSTRUCTION": "BUILD",
                    "FIRST": temp[0],
                    "SENT": time.time()}
        response = json.dumps(response)
        self.conn.send(response.encode())
        time.sleep(2)  # wait for clients to build
        self.hostGame()


if __name__ == '__main__':
    server = Server()
