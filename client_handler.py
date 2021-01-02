import socket


class ClientHandler:
    # one per client for now

    def __init__(self):
        self.conn = None

    def late_init(self, conn):
        self.conn = conn

    def establish_conn(self):
        pass
