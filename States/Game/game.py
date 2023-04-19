import pygame
from app import App
from state import State

MOVE_DIVIDER_WIDTH = 300
MOVE_DIVIDER_PADDING = 25


class Game(State):
    def __init__(self):
        super().__init__()
        self.board_divider_rect = pygame.Rect(0, 0, App.window.get_width() - MOVE_DIVIDER_WIDTH, App.window.get_height())
        self.move_divider_rect = pygame.Rect(
            self.board_divider_rect.right + MOVE_DIVIDER_PADDING, MOVE_DIVIDER_PADDING,
            MOVE_DIVIDER_WIDTH - 2 * MOVE_DIVIDER_PADDING, App.window.get_height() - 2 * MOVE_DIVIDER_PADDING
        )

        self.orig_board_image = pygame.image.load('./Assets/board.png').convert_alpha()
        board_size_ratio = (0.8 * self.move_divider_rect.height) / self.orig_board_image.get_height()
        if self.orig_board_image.get_height() * board_size_ratio <= self.board_divider_rect.width:
            self.board_image = pygame.transform.smoothscale(
                self.orig_board_image, (self.orig_board_image.get_width() * board_size_ratio,
                                        self.orig_board_image.get_height() * board_size_ratio)
            )
        else:
            new_ratio = self.board_divider_rect.width / self.orig_board_image.get_width()
            self.board_image = pygame.transform.smoothscale(
                self.orig_board_image, (self.board_divider_rect.width, self.orig_board_image.get_height() * new_ratio)
            )
        self.board_rect = self.board_image.get_rect(center=self.board_divider_rect.center)

    def resize(self, new_size):
        self.board_divider_rect = pygame.Rect(0, 0, new_size[0] - MOVE_DIVIDER_WIDTH, new_size[1])
        self.move_divider_rect = pygame.Rect(
            self.board_divider_rect.right + MOVE_DIVIDER_PADDING, MOVE_DIVIDER_PADDING,
            MOVE_DIVIDER_WIDTH - 2 * MOVE_DIVIDER_PADDING, new_size[1] - 2 * MOVE_DIVIDER_PADDING
        )

        board_size_ratio = (0.8 * self.move_divider_rect.height) / self.orig_board_image.get_height()
        if self.orig_board_image.get_height() * board_size_ratio <= self.board_divider_rect.width:
            self.board_image = pygame.transform.smoothscale(
                self.orig_board_image, (self.orig_board_image.get_width() * board_size_ratio,
                                        self.orig_board_image.get_height() * board_size_ratio)
            )
        else:
            new_ratio = self.board_divider_rect.width / self.orig_board_image.get_width()
            self.board_image = pygame.transform.smoothscale(
                self.orig_board_image, (self.board_divider_rect.width, self.orig_board_image.get_height() * new_ratio)
            )
        self.board_rect = self.board_image.get_rect(center=self.board_divider_rect.center)

    def update(self):
        self.draw()

    def draw(self):
        App.window.fill((250, 245, 240))

        pygame.draw.rect(App.window, (227, 228, 224), self.move_divider_rect)
        App.window.blit(self.board_image, self.board_rect)
