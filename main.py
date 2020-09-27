from collections import Counter

import pygame
import random

white = (255, 255, 255)
width, height = 400, 300
global board


class Board():
    def __init__(self):
        self.dis = pygame.display.set_mode((width, height))

    def updateBoard(self):
        pygame.display.update()


class Food:
    def __init__(self):
        self.food = [round(random.randrange(width - 10), -1), round(random.randrange(height), -1)]
        # food doesnt show at [400,200]
        print(self.food)
        if self.food[1] == 300:
            self.food[1] = 160
        #todo, y value of 300 doesnt show

    def draw(self):
        pygame.draw.rect(board.dis, (24, 252, 0), [self.food[0], self.food[1], 10, 10])


class Snake():
    def __init__(self, x: int, y: int, board: Board):
        self.board = board
        pygame.draw.rect(board.dis, white, [x, y, 10, 10])
        self.snake = [[x,y]]

    def draw(self, newX, newY):
        # # draw a snake
        self.snake.append([newX,newY])
        self.snake.pop(0)
        for i in self.snake:
            pygame.draw.rect(self.board.dis, white, [i[0], i[1], 10, 10])


    def eat(self, x, y):
        self.snake.append([x, y])

    def isCollision(self,x,y):
        if [x,y] in self.snake[0:len(self.snake) -1]:
            # doesnt work when size is 2
            print("herehere")
            print(self.snake)
            print([x,y])
            return True


class Game:
    @staticmethod
    def start():
        pygame.init()  # init outside class?
        global board
        board = Board()
        game_over = False
        x_change = y_change = 0

        xPosistion = 200
        yPosistion = 150
        clock = pygame.time.Clock()
        snake = Snake(xPosistion, yPosistion, board)
        food = Food()
        while not game_over:
            for event in pygame.event.get():
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
            if xPosistion > 400 or xPosistion < 0 or yPosistion > 300 or yPosistion < 0:
                print(xPosistion, yPosistion)
                game_over = True
            elif xPosistion == food.food[0] and yPosistion == food.food[1]:
                # game_over = True
                snake.eat(food.food[0],food.food[1])
                food = Food()
            elif snake.isCollision(xPosistion, yPosistion):
                Game.game_over()

            xPosistion += x_change
            yPosistion += y_change

            board.dis.fill((0, 0, 0))
            food.draw()
            snake.draw(xPosistion, yPosistion)
            pygame.display.update()
            clock.tick(15)
        game_over()
    @staticmethod
    def game_over():
        pygame.quit()
        quit()


if __name__ == '__main__':
    Game.start()
