import pygame
from app import App
from state import State
from widget import Button


class Lobby(State):
    def __init__(self):
        super().__init__()
        self.new_game_button = Button(100, 100, 200, 50, 'New Game', 'topleft')

    def update(self):
        self.new_game_button.update()

        if App.left_click:
            if self.new_game_button.hovered:
                self.done = True
                self.next = 'game'

        self.draw()

    def draw(self):
        App.window.fill((250, 245, 240))
        self.new_game_button.draw()
