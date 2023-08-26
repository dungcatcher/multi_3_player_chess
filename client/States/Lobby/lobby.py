import pygame
import json
from client.app import App
from client.state import State
from client.widget import Button, Label


class Lobby(State):
    def __init__(self):
        super().__init__()
        self.title_rect = pygame.Rect(0, 0, App.window.get_width(), App.window.get_height() * 0.2)
        self.title_label = Label(self.title_rect.left, self.title_rect.centery, self.title_rect.width, self.title_rect.height * 0.8,
                                 'Three Player Chess', 'midleft', None, None, (0, 0, 0), align='left')
        self.subtitle_label = Label(self.title_rect.left, self.title_rect.bottom, self.title_rect.width, self.title_rect.height * 0.3,
                                    'by dungcatcher', 'bottomleft', None, None, (50, 50, 50), align='left')

        self.game_select_div = pygame.Rect(0, 0, App.window.get_width() * 0.4, App.window.get_height() * 0.5)
        self.game_select_div.midtop = App.window.get_width() / 2, App.window.get_height() * 0.25
        self.game_select_buttons = []

        self.lobby_label = Label(self.game_select_div.left, self.game_select_div.top, self.game_select_div.width,
                                 self.game_select_div.height * 0.15, 'Lobby', 'bottomleft', None, (0, 0, 0), (0, 0, 0), align='center')
        self.no_games_label = Label(self.game_select_div.left, self.game_select_div.top, self.game_select_div.width,
                                    self.game_select_div.height * 0.125, 'No one is playing grrrr', 'topleft', None, None, (50, 50, 50), align='center')
        self.no_games_label.hidden = True
        self.new_game_button = Button(self.game_select_div.left, self.game_select_div.bottom, self.game_select_div.width,
                                      self.game_select_div.height * 0.15, 'New Game', 'topleft', align='center')

        self.server_games = []

    def gen_games_buttons(self):
        if not self.server_games:
            self.no_games_label.hidden = False
        else:
            self.no_games_label.hidden = True

        new_buttons = []
        for i, game in enumerate(self.server_games):
            button_label = f'{len(game["players"])} Player{"s" if len(game["players"]) > 1 else ""}: '
            for num, player in enumerate(game['players']):
                button_label += player
                if num != len(game['players']) - 1:
                    button_label += ', '

            new_button = Button(self.game_select_div.left, self.game_select_div.top + i * (0.1 * self.game_select_div.height),
                                self.game_select_div.width, self.game_select_div.height * 0.1, button_label, 'topleft', identifier=game['id'], align='left')
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
                    queue_data = {
                        'type': 'queue',
                        'data': button.identifier
                    }
                    queue_packet = json.dumps(queue_data)
                    App.client.send_packet(queue_packet)

        if App.client.last_message:
            print(App.client.last_message)
            if App.client.last_message['type'] == 'queue':
                games_data = App.client.last_message['data']
                self.server_games = games_data
                self.gen_games_buttons()
                App.client.last_message = None
            elif App.client.last_message['type'] == 'game start':
                self.done = True
                self.next = 'game'

        self.draw()

    def draw(self):
        App.window.fill((250, 245, 240))
        self.title_label.draw(App.window)
        self.subtitle_label.draw(App.window)

        self.lobby_label.draw(App.window)
        self.new_game_button.draw()
        self.no_games_label.draw(App.window)

        pygame.draw.rect(App.window, (0, 0, 0), self.game_select_div, width=1)

        for button in self.game_select_buttons:
            button.draw()
