import socket
import time
import Snake




class Server:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 8089))
        self.server_socket.listen() 
        self.conn, self.address = self.server_socket.accept()
        self.game_over = False
        self.initialized = False
        self.addresses = []
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
        while len(self.addresses) < 2:
            incoming = self.conn.recv(64)
            print(self.address)
        print("here")
            
    

