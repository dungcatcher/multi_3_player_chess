import pygame
import json
from client.app import App
from client.widget import Label, Button, TextBox
from client.state import State


class Login(State):
    def __init__(self):
        super().__init__()
        self.title_rect = pygame.Rect(0, 0, App.window.get_width(), App.window.get_height() * 0.2)
        self.title_label = Label(self.title_rect.left, self.title_rect.centery, self.title_rect.width, self.title_rect.height * 0.8,
                                 'Three Player Chess', 'midleft', None, None, (0, 0, 0), align='left')
        self.subtitle_label = Label(self.title_rect.left, self.title_rect.bottom, self.title_rect.width, self.title_rect.height * 0.3,
                                    'by dungcatcher', 'bottomleft', None, None, (50, 50, 50), align='left')

        self.spacing = 0.1 * App.window.get_height()

        self.main_div_rect = pygame.Rect(0, self.title_rect.bottom, App.window.get_width(), App.window.get_height() * 0.8)
        self.online_div_rect = pygame.Rect(0, self.main_div_rect.top, self.main_div_rect.width * 2/3, self.main_div_rect.height)
        self.offline_div_rect = pygame.Rect(self.online_div_rect.right, self.main_div_rect.top, self.main_div_rect.width * 1/3, self.main_div_rect.height)

        self.online_label = Label(self.online_div_rect.centerx, self.online_div_rect.top, 0.3 * self.online_div_rect.width,
                                  self.spacing, 'ONLINE', 'midtop', None, None, (0, 0, 0), align='center')
        self.username_input = TextBox(self.online_div_rect.centerx, self.offline_div_rect.top + self.spacing, 0.5 * self.online_div_rect.width,
                                      self.spacing, 'midtop', 'Username', align='left', hide_text=False)
        self.password_input = TextBox(self.online_div_rect.centerx, self.online_div_rect.top + self.spacing * 3, 0.5 * self.online_div_rect.width,
                                      self.spacing, 'midtop', 'Password', align='left', hide_text=True)
        self.login_button = Button(self.online_div_rect.centerx, self.offline_div_rect.top + self.spacing * 5, 0.3 * self.online_div_rect.width,
                                   self.spacing, 'Login', 'midtop', align='center')
        self.register_button = Button(self.online_div_rect.centerx, self.online_div_rect.top + self.spacing * 6.5, 0.15 * self.online_div_rect.width,
                                      self.spacing * 0.5, 'or Register', 'midtop', align='center')

        self.offline_label = Label(self.offline_div_rect.centerx, self.offline_div_rect.top, 0.3 * self.online_div_rect.width,
                                  self.spacing, 'OFFLINE', 'midtop', None, None, (0, 0, 0), align='center')
        self.offline_button = Button(self.offline_div_rect.centerx, self.offline_div_rect.top + 2 * self.spacing, 0.3 * self.online_div_rect.width,
                                     self.spacing, 'Analysis', 'midtop', align='center')

        self.error_label = Label(self.online_div_rect.centerx, self.online_div_rect.top + 2.5 * self.spacing, 0.5 * self.online_div_rect.width,
                                 0.5 * self.spacing, '', 'center', (255, 170, 170), (241, 128, 126), (241, 128, 126), align='center',
                                 border_width=2)
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
                self.next = 'analysis'
            if self.register_button.hovered:
                self.done = True
                self.next = 'register'
            if self.login_button.hovered:
                if App.client.connected:
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
                else:
                    self.error_label.hidden = False
                    self.error_label.label = 'Could not connect to server'
                    self.error_label.bg_colour = (255, 170, 170)
                    self.error_label.outline_colour = (241, 128, 126)
                    self.error_label.text_colour = (241, 128, 126)

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
                    App.client.username = self.username_input.text
                    self.done = True
                    self.next = 'menu'
                App.client.last_message = None

        self.draw()

    def draw(self):
        App.window.fill((250, 245, 240))
        self.title_label.draw(App.window)
        self.subtitle_label.draw(App.window)
        self.online_label.draw(App.window)
        self.offline_label.draw(App.window)
        self.offline_button.draw()
        self.username_input.draw()
        self.password_input.draw()
        self.login_button.draw()
        self.register_button.draw()
        self.error_label.draw(App.window)

        pygame.draw.line(App.window, (0, 0, 0), self.online_div_rect.topright, (self.online_div_rect.right, self.register_button.rect.bottom),
                         width=2)

