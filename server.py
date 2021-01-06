import time
import random
import pygame
import threading
from threading import *
from client_handler import ClientHandler
from connection_behavior import *
from lobby import Lobby
from snake_gmae_objects import Food, Snake

width = 500
height = 500
white = (255, 255, 255)


class Server:

    def __init__(self, twoPlayers=True, client_limit = 2):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 13500))
        self.server_socket.listen(2)
        self.conn = self.server_socket
        self.game_over = False
        self.initialized = False
        self.players = []
        self.twoPlayers = twoPlayers
        self.client_limit = client_limit
        self.most_recent_message = None
        self.incoming_message = None
        self.listener_flag = True
        self.ticks = {}
        self.food = None
        self.snake = None
        self.start_time = 0
        self.freeze_game = False
        self.client_handlers = []

    def start_server(self):
        # todo, handle init process inside here

        self.establish_two_connections()


    def listen(self):
        while self.listener_flag:
            response = self.conn.recv(1024)
            if len(response) > 0:
                self.most_recent_message = read_json(response)

    def establish_two_connections(self):
        # todo, create two threads and pass them two socket connections
        # todo, client limit
        response = {"INSTRUCTION": "WAIT",
                    "WIDTH": width,
                    "HEIGHT": height,
                    "WAITING": True}
        lobby = Lobby()
        while len(self.players) < 2:
            if lobby.assigned_threads == 2:
                lobby = Lobby()
            conn, address = self.conn.accept()
            self.client_handlers.append(ClientHandler(conn, lobby).start())
            lobby.assigned_threads += 1

        self.build_window_clientside()

    def build_window_clientside(self):
        self.turn = random.choice(self.players)
        self.squares = []
        x = ([1, 2], [2, 1])
        for i in range(0, width, 10):
            for j in range(0, height, 10):
                self.squares.append([i, j])
        self.squares = tuple(self.squares)

        self.snake = Snake(200, 150)
        self.food = Food(self.snake.snake, self.squares)

        response = {"INSTRUCTION": "BUILD",
                    "FIRST": self.turn,
                    "WIDTH": width,
                    "HEIGHT": height,
                    "TIME": time.time(),
                    "SNAKE": self.snake.snake,
                    "FOOD": self.food.food
                    }
        self.conn.sendall(send_json(response))
        while not self.initialized:
            # wait for both clients to report as built and ready
            players_ready = {}
            while len(players_ready) < 2:
                self.incoming_message = wait_for_message(self.conn)
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
        self.conn.sendall(send_json(message))
        players_ready = []
        while len(players_ready) < 2 or time.time() < self.start_time:
            self.incoming_message = wait_for_message(self.conn)
            if not self.twoPlayers:
                break
            elif self.incoming_message["USERNAME"] not in players_ready:
                players_ready.append(self.incoming_message["USERNAME"])



class Game(Server):
    # todo start method is a mess. does way to much. needs an init method,
    #  and packets should be analyzed in a loop from outside the game class
    def __init__(self):
        super().__init__(twoPlayers=True)
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
                    xPosistion = snake.snake[len(snake.snake) - 1][0]
                    yPosistion = snake.snake[len(snake.snake) - 1][1]
                    flag = False
                    for i in list(self.ticks.keys()):
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

            self.turn = self.players[0] if self.players[0] != self.turn else self.players[1]

            response = {"INSTRUCTION": instruction,  # CONTINUE, QUIT
                        "SNAKEPOS": snake.snake,
                        "FOODPOS": food.food,
                        "SCORE": self.score,
                        "TURN": self.turn,
                        "TIME": time.time()
                        }
            # dictionary changed size while iterating
            self.ticks[response["TIME"]] = response
            self.conn.sendall(send_json(response))
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
    server = Server()
    server.start_server()