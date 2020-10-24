import socket
import time
import json
import random
import pygame
import threading
import sys
from client import Client

width = 500
height = 500
white = (255, 255, 255)


class Server:

    def __init__(self, twoPlayers=False):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', 13500))
        self.server_socket.listen(2)
        self.conn, self.address = self.server_socket.accept()
        self.game_over = False
        self.initialized = False
        self.players = {}
        self.twoPlayers = twoPlayers
        self.most_recent_message = None
        self.is_player1_turn = False
        self.incoming_message = None
        self.listener_flag = True
        self.ticks = {}
        self.food = None
        self.snake = None
        self.start_time = 0

    def new_messsage(self):
        incoming = self.conn.recv(1024)
        if len(incoming) > 0:
            self.incoming_message = json.loads(incoming.decode())
            return True
        else:
            return False

    def listen(self):
        while self.listener_flag:
            response = self.conn.recv(1024)
            if len(response) > 0:
                self.most_recent_message = Client.read_json(response)

    def establish_two_connections(self):
        response = {"INSTRUCTION": "WAIT",
                    "WIDTH": width,
                    "HEIGHT": height,
                    "WAITING": True}

        while len(self.players) < 2:
            incoming = Client.wait_for_message(self.conn)
            temp = incoming["userName"] not in self.players
            if temp:
                self.players[incoming["userName"]] = self.address[0]
                response["WAITING"] = False if len(self.players) >= 2 else True
                response["TIME"] = time.time()

                self.conn.sendall(Client.send_json(response))
                if not self.twoPlayers:
                    break
                else:
                    pass

                # todo, breaking prematurely for the sake of testing
            else:
                response["TIME"] = time.time()
                # this function can be cleaner.
                self.conn.sendall(Client.send_json(response))

        print("ESTABLISHED TWO CONNS")
        self.build_window_clientside()

    def build_window_clientside(self):
        temp = [self.players.keys()]
        random.shuffle(temp)
        # self.is_player1_turn = temp[0]

        self.squares = []
        x = ([1, 2], [2, 1])
        for i in range(0, width, 10):
            for j in range(0, height, 10):
                self.squares.append([i, j])
        self.squares = tuple(self.squares)

        self.snake = Snake(200, 150)
        self.food = Food(self.snake.snake, self.squares)

        response = {"INSTRUCTION": "BUILD",
                    "FIRST": str(temp[0]),
                    "WIDTH": width,
                    "HEIGHT": height,
                    "TIME": time.time(),
                    "SNAKE": self.snake.snake,
                    "FOOD": self.food.food
                    }
        self.conn.sendall(Client.send_json(response))
        while not self.initialized:
            # wait for both clients to report as built and ready
            players_ready = {}
            while len(players_ready) < 2:
                self.incoming_message = Client.wait_for_message(self.conn)
                try:
                    if self.incoming_message["READY"]:
                        print("READY MESSAGE")
                        if not self.twoPlayers:
                            self.initialized = True
                            break
                        else:
                            if self.incoming_message["USERNAME"] not in players_ready:
                                players_ready[self.incoming_message["USERNAME"]] = True

                except KeyError:
                    pass
        self.sync()

    def sync(self):
        self.start_time = time.time() + .25
        message = {
            "INSTRUCTION": "PLAY",
            "STARTTIME": str(self.start_time)
        }
        self.conn.sendall(Client.send_json(message))
        players_ready = []
        while len(players_ready) < 2 or time.time() < self.start_time:
            self.incoming_message = Client.wait_for_message(self.conn)
            if not self.twoPlayers:
                break
            elif self.address not in players_ready:
                players_ready.append(self.address)



class Food:
    def __init__(self, snake, squares: tuple, pos=None):
        if pos is not None:
            self.food = pos
        else:
            self.food = self.spawnFood(squares, snake)
    def spawnFood(self, squares, snake):
        valid_squares = list(squares)
        for j in snake:
            for index, i in enumerate(valid_squares):
                if j == i:
                    valid_squares.pop(index)
        return random.choice(valid_squares)


class Snake():
    def __init__(self, x: int, y: int):
        self.snake = [[x, y]]

    def draw(self, newX, newY):
        self.snake.append([newX, newY])
        self.snake.pop(0)

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


class Game(Server):
    def __init__(self):
        super().__init__(twoPlayers=False)
        self.establish_two_connections()
        # todo, cant leave this method ^
        self.score = 0
        self.squares = []
        x = ([1, 2], [2, 1])
        for i in range(0, width, 10):
            for j in range(0, height, 10):
                self.squares.append([i, j])
        self.squares = tuple(self.squares)
        self.start()

    def start(self):
        pygame.init()
        game_over = False
        x_change = y_change = 0

        xPosistion = 200
        yPosistion = 150
        clock = pygame.time.Clock()
        snake = Snake(self.snake.snake[0][0], self.snake.snake[0][1])
        food = Food(snake.snake, self.squares, pos=self.food.food)
        # s = pygame.font.SysFont("comicsansms",25)
        while time.time() < self.start_time:
            continue
        listener = threading.Thread(target=self.listen)
        listener.start()
        while not game_over:
            event = self.most_recent_message
            if event is not None:
                if event.get("SYNC"):
                    sync_from = self.ticks[event["SYNC"]]
                    snake.snake = sync_from["SNAKEPOS"]
                    food.food = sync_from["FOODPOS"]
                    self.score = sync_from["SCORE"]
                    xPosistion = snake.snake[len(snake.snake)][0]
                    yPosistion = snake.snake[len(snake.snake)][1]
                    flag = False
                    for i in self.ticks:
                        if flag:
                            del self.ticks[i]
                        if i == sync_from["TIME"]:
                            flag = True

                else:
                    event = event["EVENT"]
                    if event == "QUIT":
                        game_over = True
                    elif event == "LEFT":
                        x_change = -10
                        y_change = 0
                    elif event == "RIGHT":
                        x_change = 10
                        y_change = 0
                    elif event == "UP":
                        x_change = 0
                        y_change = -10
                    elif event == "DOWN":
                        x_change = 0
                        y_change = 10

                    xPosistion += x_change
                    yPosistion += y_change
            # todo. when the client is spamming an input before the snake is free to move, it offsets the server snake x axis by 10

            instruction = None
            if xPosistion > width - 10 or xPosistion < 0 or yPosistion >= height or yPosistion < 0:
                instruction = "QUIT"
                print("out of bounds")
            elif [xPosistion, yPosistion] == food.food:
                snake.eat(food.food[0], food.food[1])
                self.score += 1
                food = Food(snake.snake, self.squares)
                instruction = "EAT"
                self.is_player1_turn = not self.is_player1_turn
                print("EATEN")
            elif snake.isCollision(x_change, y_change):
                instruction = "QUIT"
                print("snake collision")
            else:
                instruction = "CONTINUE"

            if instruction == "EAT":
                instruction = "CONTINUE"
            else:
                snake.draw(xPosistion, yPosistion)

            response = {"INSTRUCTION": instruction,  # CONTINUE, QUIT
                        "SNAKEPOS": snake.snake,
                        "FOODPOS": food.food,
                        "SCORE": self.score,
                        "TURN": self.is_player1_turn,  # todo, figure out turn
                        "TIME": time.time()
                        }
            self.ticks[response["TIME"]] = response
            self.conn.sendall(Client.send_json(response))
            if instruction == "QUIT":
                self.end_game()

            clock.tick(15)
        pygame.quit()
        quit()


    def end_game(self):
        self.server_socket.close()
        self.listener_flag = False
        print("ending")
        pygame.quit()
        quit()


if __name__ == '__main__':
    game = Game()
    game.start()

