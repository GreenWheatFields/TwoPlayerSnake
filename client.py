import socket
import time
import uuid
import json
import pygame
import sys
import threading
from connection_behavior import *
# #todo, small window that shows while attempting to connect. automatically closes when client receives instruction to build window


import pygame
import random

white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)
global board


class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.user_name = None
        self.width = 0
        self.height = 0
        self.ping = 0
        self.build = False
        self.first = None
        self.start_snake = None
        self.start_food = None
        self.start_time = None
        self.listener_flag = True
        self.most_recent_message = None
        self.syncing = False
        self.our_turn = None


    def listen(self):
        while self.listener_flag:
            message = self.socket.recv(1024)
            if len(message) > 0:
                try:
                    self.most_recent_message = read_json(message)
                except ValueError as v:
                    pass
                    # next_message = 0
                    # print(message.decode())  # server is skipping three ticks in front of client at times, usually when ping hits .7
                    # for index, char in enumerate(message.decode()):
                    #     if char == "}":  # todo, tell server to resynchronize at this tick/time? server will need to keep a rolling list past ticks
                    #         next_message = index
                    #         break

    def establish_connection(self):
        # self.user_name = uuid.uuid4()
        self.socket.connect(('localhost', 13500))

    def init_game(self):
        #todo, server shuold gen username. identify by ip/port?
        self.user_name = str(uuid.uuid4())
        response = {"USERNAME": self.user_name,
                    "TIME": time.time()}
        self.socket.send(send_json(response))
        while True:
            incoming = wait_for_message(self.socket) # bottleneck is here
            print(incoming)
            if incoming["INSTRUCTION"] == "BUILD":
                self.width = incoming["WIDTH"]
                self.height = incoming["HEIGHT"]
                self.first = incoming["FIRST"]
                self.start_snake = incoming["SNAKE"]
                self.start_food = incoming["FOOD"]
                self.our_turn = incoming["FIRST"] == self.user_name
                break
            elif incoming["INSTRUCTION"] == "WAIT":
                print("wait instruction")
                continue
                # self.ping = time.time() - incoming["TIME"]
                # response = {"userName": str(uuid.uuid4()),
                #             "time": time.time()}
                # self.socket.sendall(self.send_json(response))
            else:
                # error
                pass
        self.prepare_build()

    def prepare_build(self):
        # declare variables here
        # todo, notify server build was succesful
        if self.width != 0 and self.height != 0:
            self.build = True

    def notify_and_sync(self):
        message = {"READY": True,
                   "TIME": time.time(),
                   "USERNAME": self.user_name}
        self.socket.sendall(send_json(message))
        while True:
            incoming = wait_for_message(self.socket)
            if incoming["INSTRUCTION"] == "PLAY":
                self.start_time = incoming["STARTTIME"]
                break
            else:
                continue
        self.socket.sendall(send_json({"USERNAME": self.user_name}))


class Board():
    def __init__(self, width, height):
        self.dis = pygame.display.set_mode((width, height))
        pygame.display.set_caption("2PSnake")


class Food:
    def __init__(self, snake, squares: tuple, pos=None):
        if pos is not None:
            self.food = pos
        else:
            self.food = self.spawnFood(squares, snake)

    def draw(self):
        pygame.draw.rect(board.dis, (24, 252, 0), [self.food[0], self.food[1], 10, 10])

    def spawnFood(self, squares, snake):
        valid_squares = list(squares)
        for j in snake:
            for index, i in enumerate(valid_squares):
                if j == i:
                    valid_squares.pop(index)
        return random.choice(valid_squares)


class Snake:
    def __init__(self, x: int, y: int, board: Board):
        self.board = board
        pygame.draw.rect(board.dis, white, [x, y, 10, 10])
        self.snake = [[x, y]]

    def draw(self, color):
        for i in self.snake:
            pygame.draw.rect(self.board.dis, color, [i[0], i[1], 10, 10])

    def eat(self, x, y):
        self.snake.append([x, y])

    def isCollision(self, x, y):
        snake_head = self.snake[len(self.snake) - 1]
        if [snake_head[0], snake_head[1]] in self.snake[0:len(self.snake) - 1]:
            return True
        elif len(self.snake) == 2:
            if y == 0:
                if self.snake[1][0] + x == self.snake[0][0]:
                    return True
            elif x == 0:
                if self.snake[1][1] + y == self.snake[0][1]:
                    return True


class Game(Client):
    def __init__(self):
        super().__init__()
        self.establish_connection()
        self.init_game()
        while not self.build:
            continue
        self.notify_and_sync()
        self.score = 0
        self.squares = []
        x = ([1, 2], [2, 1])
        for i in range(0, self.width, 10):
            for j in range(0, self.height, 10):
                self.squares.append([i, j])
        self.squares = tuple(self.squares)
        listener = threading.Thread(target=self.listen, name="ClientListener")  # todo, somewhere in this thread is a json.decode.decode error. only here
        listener.start()
        self.start()

    def start(self):
        pygame.init()
        global board
        board = Board(self.width, self.height)
        game_over = False
        x_change = y_change = 0
        xPosistion = 200
        yPosistion = 150
        clock = pygame.time.Clock()
        snake = Snake(self.start_snake[0][0], self.start_snake[0][1], board)
        food = Food(snake.snake, self.squares, pos=self.start_food)
        ping = 0
        food.draw()
        snake.draw(white)
        pygame.display.update()
        s = pygame.font.SysFont("comicsansms", 25)
        message = "NONE"
        print("about to wait")
        while time.time() < float(self.start_time):
            continue
        while not game_over:
            if self.our_turn:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        game_over = True
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            x_change = -10
                            y_change = 0
                            message = "LEFT"
                        elif event.key == pygame.K_RIGHT:
                            x_change = 10
                            y_change = 0
                            message = "RIGHT"
                        elif event.key == pygame.K_UP:
                            x_change = 0
                            y_change = -10
                            message = "UP"
                        elif event.key == pygame.K_DOWN:
                            x_change = 0
                            y_change = 10
                            message = "DOWN"

            self.socket.sendall(send_json({"EVENT": message}))

            if self.most_recent_message is not None:
                if self.most_recent_message["INSTRUCTION"] == "CONTINUE":
                    snake.snake = self.most_recent_message["SNAKEPOS"]
                    food = Food(None, None, pos=self.most_recent_message["FOODPOS"])
                    self.score = self.most_recent_message["SCORE"]
                    ping = time.time() - self.most_recent_message["TIME"]
                    self.our_turn = self.most_recent_message["TURN"] == self.user_name
                    print(ping)
                    if (ping > 2): self.game_over()
                elif self.most_recent_message["INSTRUCTION"] == "QUIT":
                    break

            xPosistion += x_change
            yPosistion += y_change

            board.dis.fill((0, 0, 0))
            food.draw()
            snake.draw(red if self.most_recent_message is not None and self.most_recent_message["TURN"] == True else blue)
            v = s.render(str(self.score), True, white)
            board.dis.blit(v, [0, 0])

            pygame.display.update()
            clock.tick(15)
        pygame.quit()
        quit()

    def game_over(self):
        pygame.quit()
        quit()


if __name__ == '__main__':
    g = Game()
    g.start()
