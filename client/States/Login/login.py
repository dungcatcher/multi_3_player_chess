from client.app import App
from client.widget import Button
from client.state import State


class Login(State):
    def __init__(self):
        super().__init__()
        self.offline_button = Button(100, 100, 200, 50, 'Play offline', 'topleft')

    def update(self):
        self.offline_button.update()

        if App.left_click:
            if self.offline_button.hovered:
                self.done = True
                self.next = 'menu'

        self.draw()

    def draw(self):
        App.window.fill((250, 245, 240))
        self.offline_button.draw()

