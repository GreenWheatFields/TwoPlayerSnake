import socket
import time
str
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
        # check for connections before starting game
        # while not self.game_over:
        #     incoming = self.conn.recv(64)
        #     if len(incoming) > 0:
        #         print(incoming.decode())
        #         self.conn.sendall("RESPONSE".encode())
    def initializeGame(self):
        # establish two connections
        # tell clients how to build the window
        while len(self.players) < 2:
            incoming = self.conn.recv(64)
            if len(incoming) > 0:
                if incoming.decode() not in self.players:
                    self.players[incoming.decode()] = self.address[0]
                    self.conn.sendall() #for now, sendall, later sendto
                else:
                    #client querying server before intialized
                    pass

        # game width, and height
        # client should add a username on its first handshake
        # estabilsh game logic like who goes first etc
if __name__ == '__main__':
    server = Server()
            
    

