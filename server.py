from client_handler import ClientHandler
from connection_behavior import *
from lobby import Lobby

width = 500
height = 500
white = (255, 255, 255)
#
# todo, lobby needs to notify server when it dies
#     syncing behavior not inplemented


class Server:
    def __init__(self, client_limit=100):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 13500))
        self.server_socket.listen(2)
        self.conn = self.server_socket
        self.client_handlers = []
        self.limit = client_limit

    def accept_connections(self):
        lobby = Lobby()
        while len(self.client_handlers) < self.limit:
            if lobby.assigned_threads == 2:
                lobby = Lobby()
            conn, address = self.conn.accept()
            self.client_handlers.append(ClientHandler(conn, lobby).start())
            lobby.assigned_threads += 1



if __name__ == '__main__':
    server = Server()
    server.accept_connections()
