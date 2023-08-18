import pygame


class Game:
    def __init__(self):
        self.players = []
        self.waiting = True

    def add_player(self, addr):
        self.players.append(addr)
        if len(self.players) == 3:
            self.waiting = False
