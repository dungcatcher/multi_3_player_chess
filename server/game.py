import random
from chesslogic.board import Board

COLOURS = ['w', 'r', 'b']


class Game:
    def __init__(self):
        # Init
        self.player_data = {}  # username: {socket, colour}
        self.available_colours = COLOURS
        self.started = False

        # Game
        self.board = Board()

    def add_player(self, username, conn):
        self.player_data[username] = {}
        self.player_data[username]['socket'] = conn
        # Get player colour
        player_colour = random.choice(self.available_colours)
        self.available_colours.remove(player_colour)
        self.player_data[username]['colour'] = player_colour

        if len(self.player_data.keys()) == 3:
            self.started = True
