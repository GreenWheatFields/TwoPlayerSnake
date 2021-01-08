import time
from collections import Counter

import pygame
import random

white = (255, 255, 255)
global board


class Board:
    def __init__(self, width, height):
        self.dis = pygame.display.set_mode((width, height))
        pygame.display.set_caption("2PSnake")


class Food:
    def __init__(self, snake, squares: tuple, pos=None):
        if pos is not None:
            self.food = pos
        else:
            self.food = self.spawnFood(squares, snake)

    def draw(self, board):
        pygame.draw.rect(board.dis, (24, 252, 0), [self.food[0], self.food[1], 10, 10])

    def spawnFood(self, squares, snake):
        valid_squares = list(squares)
        for j in snake.snake:
            for index, i in enumerate(valid_squares):
                if j == i:
                    valid_squares.pop(index)
        return random.choice(valid_squares)


class Snake():
    def __init__(self, x: int, y: int, board, server=True):
        self.server = server
        if not server:
            self.board = board
            pygame.draw.rect(board.dis, white, [x, y, 10, 10])
        self.snake = [[x, y]]

    def draw(self, board, color, newX, newY):
        self.snake.append([newX, newY])
        self.snake.pop(0)
        if not self.server:
            for i in self.snake:
                pygame.draw.rect(board.dis, color, [i[0], i[1], 10, 10])

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


class Game:
    def __init__(self, width, height, server=True):
        self.server = server
        self.score = 0
        self.squares = []
        self.board = None
        x = ([1, 2], [2, 1])
        for i in range(0, width, 10):
            for j in range(0, height, 10):
                self.squares.append([i, j])
        self.squares = tuple(self.squares)
        self.width = width
        self.height = height
        if not server:
            self.board = Board(self.width, self.height)
        self.snake = Snake(200, 150, self.board)
        self.food = Food(self.snake, self.squares)
        self.xPos = 200
        self.yPos = 150
        self.is_game_over = False

    def start(self, event=None):
        # for now. server = True basicallt doesnt let Game() control itself while Client() does.
        def initGame():
            pygame.init()  # init outside class?
            if not self.server:
                self.font = pygame.font.SysFont("comicsansms", 25)
                self.clock = pygame.time.Clock()

        if not self.server:
            initGame()
        x_change = y_change = 0
        if not self.server:
            while not self.is_game_over:
                for event in pygame.event.get():
                    x_change, y_change = self.analyze_event(event)
                    self.check_if_legal_move(x_change, y_change)
                    self.xPos += x_change
                    self.yPos += y_change
                    if not self.server:
                        board.dis.fill((0, 0, 0))
                        self.food.draw()
                        self.snake.draw(self.xPos, self.yPos)
                        v = self.font.render(str(self.score), True, white)
                        board.dis.blit(v, [0, 0])
                        pygame.display.update()
                        self.clock.tick(15)
        else:
            x_change, y_change = self.analyze_event(event)
            #return instruction object ftom here?
            self.xPos += x_change
            self.yPos += y_change
            return self.check_if_legal_move(x_change, y_change)

        pygame.quit()
        quit()

    def analyze_event(self, event):  # return x,y change, bool?
        x_change = y_change = 0
        if not self.server:
            if event.type == pygame.QUIT:
                self.is_game_over = True
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
        elif self.server:
            if event is not None:
                if event.get("SYNC"):
                    # todo, what is xchange and ychange here?
                    sync_from = self.ticks[event["SYNC"]]
                    self.snake.snake = sync_from["SNAKEPOS"]
                    self.food.food = sync_from["FOODPOS"]
                    self.score = sync_from["SCORE"]
                    xPosistion = self.snake.snake[len(self.snake.snake) - 1][0]
                    yPosistion = self.snake.snake[len(self.snake.snake) - 1][1]
                    flag = False
                    for i in list(self.ticks.keys()):
                        if flag:
                            del self.ticks[i]
                        if i == sync_from["TIME"]:
                            flag = True
                else:
                    print("here")
                    event = event["EVENT"]
                    if event == "QUIT":
                        self.is_game_over = True
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

            return x_change, y_change

    def check_if_legal_move(self, x, y):
        instruction = "QUIT"
        if self.xPos > self.width - 10 or self.xPos < 0 or self.xPos >= self.height or self.yPos < 0:
            return self.game_over() if not self.server else True
        elif self.xPos == self.food.food[0] and self.yPos == self.food.food[1]:
            self.snake.eat(self.food.food[0], self.food.food[1])
            self.score += 1
            self.food = Food(self.snake.snake, self.squares)
            instruction = "CONTINUE"
        elif self.snake.isCollision(x, y):
            pass
        else:
            instruction = "CONTINUE"
        if not self.server:
            return self.game_over() if instruction == "QUIT" else True
        else:
            return {"INSTRUCTION": instruction,  # CONTINUE, QUIT
             "SNAKEPOS": self.snake.snake,
             "FOODPOS": self.food.food,
             "SCORE": self.score,
             "TURN": None,
             "TIME": time.time()
             }

    def game_over(self):
        pygame.quit()
        quit()


if __name__ == '__main__':
    g = Game()
    g.start()
