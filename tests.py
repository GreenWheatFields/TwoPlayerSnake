import unittest
from server import Game as server_game
from client import Game as client_game 
import threading

def test1():
    g = server_game()
    g.start()

def test2():
    g = client_game()
    g.start()
if __name__ == "__main__":
    x = threading.Thread(target=test1)
    y = threading.Thread(target=test2)
    x.start()
    y.start()