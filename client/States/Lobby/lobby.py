import pygame
import json
import pickle
import codecs
from chesslogic.game import Game
from client.app import App
from client.state import State
from client.widget import Button


class Lobby(State):
    def __init__(self):
        super().__init__()
        self.new_game_button = Button(100, 100, 200, 50, 'New Game', 'topleft')

        self.game_select_div = pygame.Rect(0, 0, App.window.get_width() * 0.4, App.window.get_height() * 0.5)
        self.game_select_div.midtop = App.window.get_width() / 2, App.window.get_height() * 0.25
        self.game_select_buttons = []

        self.server_games = {}

    def update(self):
        self.new_game_button.update()

        if App.left_click:
            if self.new_game_button.hovered:
                queue_data = {
                    'type': 'queue',
                    'data': 'new'
                }
                queue_packet = json.dumps(queue_data)
                App.client.send_packet(queue_packet)

        if App.client.last_message:
            if App.client.last_message['type'] == 'queue':
                response = App.client.last_message['data']
                games = pickle.loads(codecs.decode(response.encode(), 'base64'))
                self.server_games = games

                App.client.last_message = None

        for game_id, game in self.server_games.items():
            print(game.players)

        self.draw()

    def draw(self):
        App.window.fill((250, 245, 240))
        self.new_game_button.draw()
