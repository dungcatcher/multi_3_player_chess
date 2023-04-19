import pygame
from app import App
from widget import Button
from state import State


class Menu(State):
    def __init__(self):
        super().__init__()
        self.play_button = Button(100, 100, 200, 50, 'Play', 'topleft')

    def update(self):
        self.play_button.update()

        if App.left_click:
            if self.play_button.hovered:
                self.done = True
                self.next = 'lobby'

        self.draw()

    def draw(self):
        App.window.fill((250, 245, 240))
        self.play_button.draw()

