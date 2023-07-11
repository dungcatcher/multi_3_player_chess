from client.app import App
from client.widget import Button
from client.state import State


class Menu(State):
    def __init__(self):
        super().__init__()
        self.solo_button = Button(100, 100, 200, 50, 'Play solo', 'topleft')
        self.multi_button = Button(100, 200, 300, 50, 'Play with friends', 'topleft')

    def update(self):
        self.solo_button.update()
        self.multi_button.update()

        if App.left_click:
            if self.solo_button.hovered:
                self.done = True
                self.next = 'game'

        if App.left_click:
            if self.multi_button.hovered:
                self.done = True
                self.next = 'lobby'

        self.draw()

    def draw(self):
        App.window.fill((250, 245, 240))
        self.solo_button.draw()
        self.multi_button.draw()

