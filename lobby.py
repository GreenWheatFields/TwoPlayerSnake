# game state here. acsessed by two clientlisteners
import time
from threading import Lock
import random
import sys
# todo, no need for this to be in server class. also these classes should have  server=False
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
        # begin game here. clients freeze here
        # todo, check for timeour

    def run_game(self):
        while time.time() < self.start_time:
            pass
        #senf the snake moving up . dont wait for user input to start game
        while True:
            clock = time.clock()
            self.game.start()
            # self.game.
            pass

        pass


    def run_game(self):
        pass


