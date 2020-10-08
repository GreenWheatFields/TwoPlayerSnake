import socket
import time
import uuid
import json
import pygame
import sys


# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect(('localhost', 8089))
# usename = str(uuid.uuid4())
# s.send(usename.encode())
# pygame.init()
# while True:
#     print(pygame.event.get())
#     # s.send(str(uuid.uuid4()).encode())
#     # time.sleep(1)
#
#
# #todo, small window that shows while attempting to connect. automatically closes when client receives instruction to build window
#
#
# # while True:
# #     print("here")
# #     s.send(str(time.time()).encode())
#     # incoming = s.recv(64)
#     # if len(incoming) > 0:
#     #     print(incoming.decode())
from collections import Counter

import pygame
import random

white = (255, 255, 255)
width, height = 500, 500
global board


class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.user_name = None
        self.width = 0
        self.height = 0
        self.ping = 0
        # self.to_json = lambda x: json.dumps(x).encode()

    @staticmethod
    def send_json(x):
        return json.dumps(x).encode()

    @staticmethod
    def read_json(x):
        return json.loads(x.decode())
    # @staticmethod
    # def wait_for_input(socket: socket.socket):
    #     while True:
    #         incoming = socket.recv(1024)
    #         if len(incoming) > 0:
    #             incoming.decode()
    #             return True
            

    def establish_connection(self):
        # self.user_name = uuid.uuid4()
        self.socket.connect(('localhost', 8089))

    def init(self):
        response = {"userName": str(uuid.uuid4()),
                    "time": time.time()}
        response = json.dumps(response).encode()
        self.socket.send(response)
        while True:
            incoming = self.socket.recv(1024)
            if len(incoming) > 0:
                incoming = self.read_json(incoming)
                print(incoming)
                if incoming["INSTRUCTION"] == "BUILD":
                    print("here")
                    if self.width != 0 and self.height != 0:
                        break
                    pass
                elif incoming["INSTRUCTION"] == "WAIT":
                    print("here2")
                    # parse then/ wait for response
                    self.width = incoming["WIDTH"]
                    self.height = incoming["HEIGHT"]
                    self.ping = time.time() - incoming["TIME"]
                    response = {"userName": str(uuid.uuid4()),
                                "time": time.time()}
                    self.socket.sendall(self.send_json(response))
                else:
                    # error
                    pass
        self.init_build()

    def init_build(self):
        print("BUILDING")
        sys.exit()
        # parse start time, window size, snake position, other player name, ping, etc


class Board():
    def __init__(self):
        self.dis = pygame.display.set_mode((width, height))
        pygame.display.set_caption("2PSnake")


class Food:
    def __init__(self, snake, squares: tuple):
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


class Snake():
    def __init__(self, x: int, y: int, board: Board):
        self.board = board
        pygame.draw.rect(board.dis, white, [x, y, 10, 10])
        self.snake = [[x, y]]

    def draw(self, newX, newY):
        self.snake.append([newX, newY])
        self.snake.pop(0)
        for i in self.snake:
            pygame.draw.rect(self.board.dis, white, [i[0], i[1], 10, 10])

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
        self.init()
        self.score = 0
        self.squares = []
        x = ([1, 2], [2, 1])
        for i in range(0, width, 10):
            for j in range(0, height, 10):
                self.squares.append([i, j])
        self.squares = tuple(self.squares)

    def start(self):
        pygame.init()  # init outside class?
        global board
        board = Board()
        game_over = False
        x_change = y_change = 0

        xPosistion = 200
        yPosistion = 150
        clock = pygame.time.Clock()
        snake = Snake(xPosistion, yPosistion, board)
        food = Food(snake.snake, self.squares)
        s = pygame.font.SysFont("comicsansms", 25)

        while not game_over:
            for event in pygame.event.get():
                print(event)
                if event.type == pygame.QUIT:
                    game_over = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        x_change = -10
                        y_change = 0
                    elif event.key == pygame.K_RIGHT:
                        x_change = 10
                        y_change = 0
                    elif event.key == pygame.K_UP:
                        x_change = 0
                        y_change = -10
                    elif event.key == pygame.K_DOWN:
                        x_change = 0
                        y_change = 10
            print(xPosistion, yPosistion)
            if xPosistion > width - 10 or xPosistion < 0 or yPosistion >= height or yPosistion < 0:
                self.game_over()
            elif xPosistion == food.food[0] and yPosistion == food.food[1]:
                snake.eat(food.food[0], food.food[1])
                self.score += 1
                food = Food(snake.snake, self.squares)
            elif snake.isCollision(x_change, y_change):
                self.game_over()

            xPosistion += x_change
            yPosistion += y_change

            board.dis.fill((0, 0, 0))
            food.draw()
            snake.draw(xPosistion, yPosistion)

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
