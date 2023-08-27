from client.app import App
from client.widget import Button, TextBox
from client.state import State
from client.app_client import AppClient


class Address(State):
    def __init__(self):
        super().__init__()
        self.address_box = TextBox(App.window.get_width() / 2, App.window.get_height() / 2, App.window.get_width() * 0.4,
                                   App.window.get_height() * 0.1, 'midbottom', 'Address of server', align='left')
        self.enter_button = Button(self.address_box.rect.centerx, self.address_box.rect.bottom + 0.1 * App.window.get_height(),
                                   App.window.get_width() * 0.3, App.window.get_height() * 0.1, 'Enter', 'midtop', align='center')

    def get_event(self, event):
        self.address_box.handle_event(event)

    def update(self):
        self.address_box.update()
        self.enter_button.update()

        if App.left_click:
            if self.enter_button.hovered:
                App.client = AppClient(self.address_box.text)

                self.done = True
                self.next = 'login'
            if self.address_box.hovered:
                self.address_box.selected = True

        self.draw()

    def draw(self):
        App.window.fill((250, 245, 240))

        self.address_box.draw()
        self.enter_button.draw()
