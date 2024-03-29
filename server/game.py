import random
from chesslogic.board import Board
import time


class Game:
    def __init__(self):
        # Init
        self.player_data = {}  # username: {socket, colour, time}
        self.available_colours = ['w', 'r', 'b']
        self.started = False

        self.start_timer = False
        self.previous_time = None

        self.turn = None  # Username
        # Game
        self.board = Board()

    def update(self):
        if self.start_timer:
            delta_time = time.time() - self.previous_time
            if self.turn in self.player_data.keys():  # Just in case
                self.player_data[self.turn]['time'] -= delta_time
            self.previous_time = time.time()

    def add_player(self, username, conn):
        self.player_data[username] = {}
        self.player_data[username]['socket'] = conn
        # Get player colour
        player_colour = random.choice(self.available_colours)
        self.available_colours.remove(player_colour)
        self.player_data[username]['colour'] = player_colour
        self.player_data[username]['time'] = 300

        if len(self.player_data.keys()) == 3:
            self.started = True

