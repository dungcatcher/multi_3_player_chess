import pygame
import json
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

        self.server_games = []

    def gen_games_buttons(self):
        new_buttons = []
        for i, game in enumerate(self.server_games):
            new_button = Button(self.game_select_div.left, self.game_select_div.top + i * (0.1 * self.game_select_div.height),
                                self.game_select_div.width, self.game_select_div.height * 0.1, game['id'], 'topleft', identifier=game['id'], align='left')
            new_buttons.append(new_button)
        self.game_select_buttons = new_buttons

    def update(self):
        self.new_game_button.update()
        for button in self.game_select_buttons:
            button.update()

        if App.left_click:
            if self.new_game_button.hovered:
                queue_data = {
                    'type': 'queue',
                    'data': 'new'
                }
                queue_packet = json.dumps(queue_data)
                App.client.send_packet(queue_packet)
            for button in self.game_select_buttons:
                if button.hovered:
                    print(button.identifier)

        if App.client.last_message:
            if App.client.last_message['type'] == 'queue':
                games_data = App.client.last_message['data']
                self.server_games = games_data
                self.gen_games_buttons()
                App.client.last_message = None

        self.draw()

    def draw(self):
        App.window.fill((250, 245, 240))
        self.new_game_button.draw()
        for button in self.game_select_buttons:
            button.draw()
