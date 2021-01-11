# game state here. acsessed by two clientlisteners
import time
from threading import Lock
import random
import sys
import pygame as pyg
from connection_behavior import *
from snake_gmae_objects import Snake, Food, Game


class Lobby():
    def __init__(self):
        super().__init__()
        self._lock = Lock()
        self.handlers = {}
        self.players = []
        self.assigned_threads = 0
        self.turn = None
        self.init_flag = False
        self.squares = []
        self.snake = None
        self.food = None
        self.players_ready = []
        self.game = None
        self.start_time = 9

    def acquire(self):
        self._lock.acquire()

    def release(self):
        self._lock.release()

    def init_game_state(self, width: int, height: int):
        self.game = Game(width, height)
        self.turn = random.choice(self.players)
        self.init_flag = True

    def notify_player_ready(self, username: str):
        if username not in self.players_ready:
            self.players_ready.append(username)

    def sync(self):
        self.players_ready = []
        self.start_time = time.time() + .25
        for client_handler in self.handlers.values():
            client_handler.send_sync_message(self.start_time)
        while len(self.players_ready) < 2 and time.time() < self.start_time:
            for client_handler in self.handlers.values():
                if client_handler.synced:
                    if client_handler.username not in self.players_ready:
                        self.players_ready.append(client_handler.username)
        self.run_game()

    def run_game(self):
        #clients freeze here/ have weird behavior
        players = []
        cur_handler = None
        turn = 0
        for index, client_handler in enumerate(self.handlers.keys()):
            self.handlers[client_handler].listen()
            players.append(self.handlers[client_handler])
            if client_handler == self.turn:
                turn = index
                cur_handler = self.handlers[client_handler]
        while time.time() < self.start_time:
            pass
        #senf the snake moving up . dont wait for user input to start game
        while self.init_flag:
            clock = pyg.time.Clock()
            event = cur_handler.most_recent_message
            if event is not None:
                event = read_json(event)
            #save ticks here?
            message = self.game.start(event)
            if type(message) is bool:
                #todo, game over behavior
                self.clean_up_and_leave()
                break
            message["TURN"] = cur_handler.username
            if message["INSTRUCTION"] == "EAT":
                for i in self.handlers.keys():
                    if i != cur_handler.username:
                        turn = int(not turn)
                        cur_handler = players[turn]
                        break
                message["TURN"] = cur_handler.username
                message["INSTRUCTION"] = "CONTINUE"
            for client_handler in self.handlers.values():
                try:
                    client_handler.conn.sendall(send_json(message))
                except ConnectionError:
                    self.clean_up_and_leave()
            clock.tick(15)

    def clean_up_and_leave(self):
        for handler in self.handlers.values():
            self.init_flag = False
            handler.flag = False
            handler.conn.close()


