# game state here. acsessed by two clientlisteners
import time
from threading import Lock
import random
import sys
# todo, no need for this to be in server class. also these classes should have  server=False
# from server import Snake, Food


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

    def acquire(self):
        self._lock.acquire()
    def release(self):
        self._lock.release()
    def init_game_state(self, width, height):
        self.turn = random.choice(self.players)
        temp = []
        for i in range(0, width, 10):
            for j in range(0, height, 10):
                temp.append([i, j])
        self.squares = tuple(temp)
        # self.snake = Snake(200, 150)
        # self.food = Food(self.snake.snake, self.squares)
        self.init_flag = True

    def notify_player_ready(self, username: str):
        if username not in self.players_ready:
            self.players_ready.append(username)
    def sync(self):
        sys
        # start_time = time.time() + .25
        # for client_handler in self.handlers.values():
        #     pass
        # while len(players_ready) < 2 or time.time() < self.start_time:
        #     self.incoming_message = wait_for_message(self.conn)
        #     if not self.twoPlayers:
        #         break
        #     elif self.incoming_message["USERNAME"] not in players_ready:
        #         players_ready.append(self.incoming_message["USERNAME"])
    def run_game(self):
        pass
