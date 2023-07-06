import pygame
from app import App
from state import State

"""
Resiszing:

Board and move table always in the center
Player names at the top
CLock at the bottom

Board + clock + player names = height of window
Board minimum size - TBD
Move divider minimum size

Main div
Move divider

"""
SIDE_PADDING = 25

CLOCK_HEIGHT = 75
MIN_HEIGHT = 540
MOVE_DIVIDER_MIN_WIDTH = 250
MOVE_DIVIDER_MAX_WIDTH = 350


class Game(State):
    def __init__(self):
        super().__init__()
        self.piece_image_dict = {}
        self.load_spritesheet()

        self.orig_board_image = pygame.image.load('./Assets/board.png').convert_alpha()

        # Initialised in resize function
        self.board_image = None
        self.main_rect = None
        self.playing_divider_rect = None
        self.move_divider_rect = None
        self.players_divider_rect = None
        self.clock_divider_rect = None
        self.board_rect = None

        self.place_elements()

    def load_spritesheet(self):
        piece_size = 135
        chess_sprite_image = pygame.image.load('./Assets/chess_pieces.png').convert_alpha()

        piece_letters = ['k', 'q', 'b', 'n', 'r', 'p']
        piece_colours = ['w', 'b', 'r']
        for col, letter in enumerate(piece_letters):
            for row, colour in enumerate(piece_colours):
                piece_rect = pygame.Rect(col * piece_size, row * piece_size, piece_size, piece_size)
                piece_surface = pygame.Surface((piece_size, piece_size), pygame.SRCALPHA, 32)
                piece_surface.blit(chess_sprite_image, (0, 0), piece_rect)

                self.piece_image_dict[colour + letter] = piece_surface

    def place_elements(self):
        main_height = App.window.get_height() - 2 * SIDE_PADDING

        board_height = main_height - 2 * CLOCK_HEIGHT
        board_scale = board_height / self.orig_board_image.get_height()
        board_width = self.orig_board_image.get_width() * board_scale
        self.board_image = pygame.transform.smoothscale(self.orig_board_image, (board_width, board_height))

        test_move_divider_width = (App.window.get_width() - 2 * SIDE_PADDING) - board_width - SIDE_PADDING
        # Constrain to max and min sizes
        move_divider_width = test_move_divider_width
        if test_move_divider_width > MOVE_DIVIDER_MAX_WIDTH:
            move_divider_width = MOVE_DIVIDER_MAX_WIDTH
        elif test_move_divider_width < MOVE_DIVIDER_MIN_WIDTH:
            move_divider_width = MOVE_DIVIDER_MIN_WIDTH

        self.main_rect = pygame.Rect(0, 0, move_divider_width + board_width + SIDE_PADDING, main_height)
        self.main_rect.center = (App.window.get_width() / 2, App.window.get_height() / 2)

        self.playing_divider_rect = pygame.Rect(*self.main_rect.topleft, board_width, main_height)
        self.move_divider_rect = pygame.Rect(0, 0, move_divider_width, main_height)
        self.move_divider_rect.topright = self.main_rect.topright
        self.players_divider_rect = pygame.Rect(*self.main_rect.topleft, self.playing_divider_rect.width, CLOCK_HEIGHT)
        self.board_rect = pygame.Rect(*self.players_divider_rect.bottomleft, self.playing_divider_rect.width, board_height)
        self.clock_divider_rect = pygame.Rect(*self.board_rect.bottomleft, self.playing_divider_rect.width, CLOCK_HEIGHT)

    def resize(self, new_size):
        self.place_elements()

    def update(self):
        self.draw()

    def draw(self):
        App.window.fill((250, 245, 240))

        pygame.draw.rect(App.window, (227, 228, 224), self.move_divider_rect)
        App.window.blit(self.board_image, self.board_rect)
