# game state here. acsessed by two clientlisteners
class Lobby:
    def __init__(self):
        self.players = []
        self.assigned_threads = 0