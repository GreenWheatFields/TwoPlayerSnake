import socket
import time

from lobby import Lobby
from threading import Thread
from connection_behavior import *


class ClientHandler(Thread):
    # one per client for now

    def __init__(self, conn: socket.socket, lobby: Lobby):
        super().__init__()
        self.conn = None
        self.lobby = lobby
        self.width = 500
        self.height = 500

    def establish_conn(self):
        pass

    def make_first_contact(self):
        response = {"INSTRUCTION": "WAIT",
                    "WIDTH": self.width,
                    "HEIGHT": self.height,
                    "WAITING": True}

        incoming = wait_for_message(self.conn)
        temp = incoming["USERNAME"] not in self.lobby.players
        if temp:
            self.lobby.players.append(incoming["USERNAME"])
            response["WAITING"] = False if len(self.lobby.players) >= 2 else True
            response["TIME"] = time.time()

            self.conn.sendto(send_json(response), self.address)
            if not self.twoPlayers:
                # break
                pass
            else:
                pass

        else:
            response["TIME"] = time.time()
            # this function can be cleaner.
            self.conn.sendall(send_json(response))

    def run(self):
        pass
