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
        self.selected_image = None
        self.rect = None
        self.original_pixel_pos = None
        self.gen_image(game)

        # For sliding piece animation
        self.is_moving = False
        self.target_pixel_pos = None
        self.slide_amount = 0

        self.selected = False
        self.moves = []

    def gen_image(self, game):
        self.normal_image = pygame.transform.smoothscale(
            self.orig_image, (0.07 * game.board_image.get_height(), 0.07 * game.board_image.get_height())
        )
        self.selected_image = pygame.transform.smoothscale(
            self.orig_image, (0.1 * game.board_image.get_height(), 0.1 * game.board_image.get_height())
        )
        self.image = self.normal_image

        polygon = game.segment_polygons[self.pos.segment][int(self.pos.square.y * 8 + self.pos.square.x)]
        polygon = shapely.Polygon(polygon)
        self.rect = self.image.get_rect(center=(polygon.centroid.x, polygon.centroid.y))
        self.original_pixel_pos = (polygon.centroid.x, polygon.centroid.y)
