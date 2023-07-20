import pygame
import shapely


def lerp(v0, v1, t):
    return v0 + t * (v1 - v0)


def lerp2d(pos0, pos1, t):
    return lerp(pos0[0], pos1[0], t), lerp(pos0[1], pos1[1], t)


class GraphicalPiece:
    def __init__(self, piece_id, pos, image, game):
        # take in position argument and piece_id, calculates image and rect based on it
        self.piece_id = piece_id
        self.orig_image = image
        self.pos = pos

        self.image = None
        self.normal_image = None
        self.ghost_image = None
        self.ghost_rect = None
        self.selected_image = None
        self.rect = None
        self.original_pixel_pos = None
        self.gen_image(game)

        # For sliding piece animation
        self.is_moving = False
        self.target_pixel_pos = None
        self.slide_amount = 0

        self.dead = False

        self.picked_up = False
        self.moves = []

    def do_move(self, end_pixel_pos, is_drop):
        if is_drop:
            self.original_pixel_pos = end_pixel_pos
            self.rect.center = end_pixel_pos
            self.ghost_rect.center = end_pixel_pos
        else:  # Do animation
            self.is_moving = True
            self.target_pixel_pos = end_pixel_pos

    def do_animation(self):
        self.slide_amount += 0.1
        self.rect.center = lerp2d(self.original_pixel_pos, self.target_pixel_pos, self.slide_amount)

        if self.slide_amount >= 1:
            self.rect.center = self.target_pixel_pos
            self.ghost_rect.center = self.target_pixel_pos
            self.original_pixel_pos = self.target_pixel_pos
            self.slide_amount = 0
            self.target_pixel_pos = None
            self.is_moving = False

    def gen_image(self, game):
        self.normal_image = pygame.transform.smoothscale(
            self.orig_image, (0.07 * game.board_image.get_height(), 0.07 * game.board_image.get_height())
        )
        self.selected_image = pygame.transform.smoothscale(
            self.orig_image, (0.1 * game.board_image.get_height(), 0.1 * game.board_image.get_height())
        )
        self.ghost_image = self.normal_image.copy()
        self.ghost_image.set_alpha(128)
        self.image = self.normal_image

        polygon = game.segment_polygons[self.pos.segment][int(self.pos.square.y * 8 + self.pos.square.x)]
        polygon = shapely.Polygon(polygon)
        self.rect = self.image.get_rect(center=(polygon.centroid.x, polygon.centroid.y))
        self.ghost_rect = self.rect.copy()
        self.original_pixel_pos = (polygon.centroid.x, polygon.centroid.y)
