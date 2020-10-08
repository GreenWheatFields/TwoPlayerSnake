from collections import Counter

import pygame
import random

white = (255, 255, 255)
width, height = 500, 500
global board


class Board():
    def __init__(self):
        self.dis = pygame.display.set_mode((width, height))
        pygame.display.set_caption("2PSnake")

class Food:
    def __init__(self, snake, squares: tuple):
        self.food = self.spawnFood(squares, snake)

    def draw(self):
        pygame.draw.rect(board.dis, (24, 252, 0), [self.food[0], self.food[1], 10, 10])
    
    def spawnFood(self ,squares, snake):
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


class Game:
    def __init__(self):
        self.score = 0
        self.squares = []
        x = ([1,2], [2,1])
        for i in range(0,width, 10):
            for j in range(0,height, 10):
                self.squares.append([i,j])
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
        s = pygame.font.SysFont("comicsansms",25)

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
