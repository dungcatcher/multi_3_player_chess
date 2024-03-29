import pygame
import json
from client.app import App
from client.widget import Label, Button, TextBox
from client.state import State


class Register(State):
    def __init__(self):
        super().__init__()
        self.main_div_rect = pygame.Rect(0, 0, App.window.get_width() * 0.3, App.window.get_height() * 0.5)
        self.main_div_rect.center = App.window.get_width() / 2, App.window.get_height() / 2

        self.username_input = TextBox(self.main_div_rect.left, self.main_div_rect.top, self.main_div_rect.width, self.main_div_rect.height * 0.15,
                                      'topleft', 'Username', align='left', hide_text=False)
        self.password_input = TextBox(self.main_div_rect.left, self.main_div_rect.top + self.main_div_rect.height * 0.2, self.main_div_rect.width,
                                      self.main_div_rect.height * 0.15, 'topleft', 'Password', align='left', hide_text=True)
        self.password_confirmation_input = TextBox(self.main_div_rect.left, self.main_div_rect.top + self.main_div_rect.height * 0.4, self.main_div_rect.width,
                                      self.main_div_rect.height * 0.15, 'topleft', 'Confirm Password', align='left', hide_text=True)
        self.register_button = Button(self.main_div_rect.centerx, self.main_div_rect.top + self.main_div_rect.height * 0.6, self.main_div_rect.width * 0.4,
                                      self.main_div_rect.height * 0.15, 'Register', 'midtop', align='center')

        self.error_label = Label(self.main_div_rect.x, self.main_div_rect.top - 0.05 * self.main_div_rect.height, self.main_div_rect.width, self.main_div_rect.height * 0.2,
                                 '', 'bottomleft', (255, 170, 170), (241, 128, 126), (241, 128, 126), align='left', border_width=3)
        self.error_label.hidden = True

        self.back_button = Button(50, 50, App.window.get_width() * 0.1, App.window.get_height() * 0.05, 'Back', 'topleft', align='left')

    def get_event(self, event):
        self.username_input.handle_event(event)
        self.password_input.handle_event(event)
        self.password_confirmation_input.handle_event(event)

    """Use functions for error labels"""
    def update(self):
        self.username_input.update()
        self.password_input.update()
        self.password_confirmation_input.update()
        self.register_button.update()
        self.back_button.update()

        if App.left_click:
            self.username_input.selected = False
            self.password_input.selected = False
            self.password_confirmation_input.selected = False

            if self.register_button.hovered:
                if App.client.connected:
                    if self.password_input.text == self.password_confirmation_input.text:
                        register_data = {
                            'username': self.username_input.text,
                            'password': self.password_input.text
                        }
                        json_packet = json.dumps(register_data)
                        packet_data = {
                            'type': 'register',
                            'data': json_packet
                        }
                        packet_json = json.dumps(packet_data)
                        App.client.send_packet(packet_json)
                    else:
                        self.error_label.hidden = False
                        self.error_label.bg_colour = (255, 170, 170)
                        self.error_label.outline_colour = (241, 128, 126)
                        self.error_label.text_colour = (241, 128, 126)
                        self.error_label.label = 'Passwords do not match'
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
            if self.password_confirmation_input.hovered:
                self.password_confirmation_input.selected = True

            if self.back_button.hovered:
                self.done = True
                self.next = 'login'

        if App.client.last_message:
            if App.client.last_message['type'] == 'register':
                if App.client.last_message['data'] == 'created':  # Successful
                    self.error_label.hidden = False
                    self.error_label.label = 'Account created successfully'
                    self.error_label.bg_colour = (170, 255, 170)
                    self.error_label.outline_colour = (128, 241, 126)
                    self.error_label.text_colour = (128, 241, 126)
                else:
                    self.error_label.hidden = False
                    self.error_label.label = 'Account already exists'
                    self.error_label.bg_colour = (255, 170, 170)
                    self.error_label.outline_colour = (241, 128, 126)
                    self.error_label.text_colour = (241, 128, 126)
                App.client.last_message = None

        self.draw()

    def draw(self):
        App.window.fill((250, 245, 240))
        self.username_input.draw()
        self.password_input.draw()
        self.password_confirmation_input.draw()
        self.register_button.draw()
        self.error_label.draw(App.window)
        self.back_button.draw()

    def reset(self):
        self.error_label.hidden = True
