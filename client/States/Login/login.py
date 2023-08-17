import pygame
import json
from client.app import App
from client.widget import Label, Button, TextBox
from client.state import State


class Login(State):
    def __init__(self):
        super().__init__()
        self.offline_button = Button(100, 100, 200, 50, 'Play offline', 'topleft')
        self.main_div_rect = pygame.Rect(0, 0, App.window.get_width() * 0.3, App.window.get_height() * 0.5)
        self.main_div_rect.center = App.window.get_width() / 2, App.window.get_height() / 2

        self.username_input = TextBox(self.main_div_rect.left, self.main_div_rect.top, self.main_div_rect.width, self.main_div_rect.height * 0.15,
                                      'topleft', 'Username', align='left', hide_text=False)
        self.password_input = TextBox(self.main_div_rect.left, self.main_div_rect.top + self.main_div_rect.height * 0.2, self.main_div_rect.width,
                                      self.main_div_rect.height * 0.15, 'topleft', 'Password', align='left', hide_text=True)
        self.login_button = Button(self.main_div_rect.centerx, self.main_div_rect.top + self.main_div_rect.height * 0.4, self.main_div_rect.width * 0.4,
                                   self.main_div_rect.height * 0.15, 'Login', 'midtop', align='center')
        self.register_button = Button(self.main_div_rect.centerx, self.main_div_rect.top + self.main_div_rect.height * 0.6,
                                   self.main_div_rect.width * 0.4,
                                   self.main_div_rect.height * 0.15, 'Register', 'midtop', align='center')

        self.error_label = Label(self.main_div_rect.x, self.main_div_rect.top - 0.05 * self.main_div_rect.height,
                                 self.main_div_rect.width, self.main_div_rect.height * 0.2,
                                 '', 'bottomleft', (255, 170, 170), (241, 128, 126), (241, 128, 126), align='left',
                                 border_width=3)
        self.error_label.hidden = True

    def get_event(self, event):
        self.username_input.handle_event(event)
        self.password_input.handle_event(event)

    def update(self):
        self.offline_button.update()
        self.username_input.update()
        self.password_input.update()
        self.login_button.update()
        self.register_button.update()

        if App.left_click:
            self.username_input.selected = False
            self.password_input.selected = False

            if self.offline_button.hovered:
                self.done = True
                self.next = 'menu'
            if self.register_button.hovered:
                self.done = True
                self.next = 'register'
            if self.login_button.hovered:
                login_data = {
                    'username': self.username_input.text,
                    'password': self.password_input.text
                }
                json_packet = json.dumps(login_data)
                packet_data = {
                    'type': 'login',
                    'data': json_packet
                }
                packet_json = json.dumps(packet_data)
                App.client.send_packet(packet_json)

            if self.username_input.hovered:
                self.username_input.selected = True
            if self.password_input.hovered:
                self.password_input.selected = True

        if App.client.last_message:
            if App.client.last_message['type'] == 'login':
                if App.client.last_message['data'] == 'not found':
                    self.error_label.hidden = False
                    self.error_label.label = 'Account does not exist'
                    self.error_label.bg_colour = (255, 170, 170)
                    self.error_label.outline_colour = (241, 128, 126)
                    self.error_label.text_colour = (241, 128, 126)
                if App.client.last_message['data'] == 'incorrect password':
                    self.error_label.hidden = False
                    self.error_label.label = 'Username or password is incorrect'
                    self.error_label.bg_colour = (255, 170, 170)
                    self.error_label.outline_colour = (241, 128, 126)
                    self.error_label.text_colour = (241, 128, 126)
                if App.client.last_message['data'] == 'logged in':
                    App.client.logged_in = True
                    self.done = True
                    self.next = 'menu'
                App.client.last_message = None

        self.draw()

    def draw(self):
        App.window.fill((250, 245, 240))
        self.offline_button.draw()
        self.username_input.draw()
        self.password_input.draw()
        self.login_button.draw()
        self.register_button.draw()
        self.error_label.draw()

