import pygame


class Game:
    def __init__(self):
        self.players = []
        self.started = False

    def add_player(self, conn):
        self.players.append(conn)
        if len(self.players) == 2:
            self.started = True
