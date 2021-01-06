import socket
import time
import random

from lobby import Lobby
from threading import Thread
from connection_behavior import *


class ClientHandler(Thread):
    # one per client for now
    # ideally, there would be one send method that takes a message / response behavior parameter. but wwhatever

    def __init__(self, conn: socket.socket, lobby: Lobby):
        super().__init__()
        self.conn = conn
        self.lobby = lobby
        self.width = 500
        self.height = 500
        self.username = ""
        self.synced = False
        self.flag = True
        self.most_recent_message = None

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
            self.lobby.acquire()
            self.lobby.players.append(incoming["USERNAME"])
            self.lobby.handlers[incoming["USERNAME"]] = self
            response["WAITING"] = False if len(self.lobby.players) >= 2 else True
            self.lobby.release()
            response["TIME"] = time.time()
            self.conn.send(send_json(response))
        else:
            response["TIME"] = time.time()
            self.conn.sendall(send_json(response))

    def send_build_instruction(self):
        self.lobby.acquire()
        if not self.lobby.init_flag:
            self.lobby.init_game_state(self.width, self.height)
        response = {"INSTRUCTION": "BUILD",
                    "FIRST": self.lobby.turn,
                    "WIDTH": self.width,
                    "HEIGHT": self.height,
                    "TIME": time.time(),
                    "SNAKE": self.lobby.game.snake.snake,
                    "FOOD": self.lobby.game.food.food
                    }
        self.conn.send(send_json(response))
        self.lobby.release()

    def wait_for_client_to_build(self):
        print("here1")
        flag = False
        while True:
            incoming_message = wait_for_message(self.conn)
            self.lobby.acquire()
            try:
                if incoming_message["READY"]:
                    self.lobby.notify_player_ready(incoming_message["USERNAME"])
                    break
            except KeyError:
                pass
        flag = len(self.lobby.players_ready) == 2
        self.lobby.release()
        if flag:
            print("here")
            self.lobby.sync()

    def send_sync_message(self, time):
        message = {
            "INSTRUCTION": "PLAY",
            "STARTTIME": str(time)
        }
        self.conn.send(send_json(message))
        response = wait_for_message(self.conn)
        # assume correct response
        self.synced = True
    def listen(self):
        #main loop
        while self.flag:
            self.most_recent_message = self.conn.recv(1024)



    def run(self):
        self.make_first_contact()
        while len(self.lobby.players) < 2:
            pass
        self.send_build_instruction()
        self.wait_for_client_to_build()
