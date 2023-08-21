import pygame
import shapely
import json
from client.app import App
from client.state import State
from .polygon import gen_polygons, resize_polygons
from .graphical_piece import GraphicalPiece
from chesslogic.classes import Position, json_to_move_obj
from chesslogic.board import Board
from chesslogic.movegen import piece_movegen

# https://websockets.readthedocs.io/en/stable/intro/tutorial1.html

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
        self.graphical_pieces = []
        self.board = Board()

        self.orig_board_image = pygame.image.load('./Assets/board.png').convert_alpha()

        # Initialised in resize function
        self.board_image: pygame.image
        self.board_scale = 1
        self.main_rect: pygame.Rect
        self.playing_divider_rect: pygame.Rect
        self.move_divider_rect: pygame.Rect
        self.players_divider_rect: pygame.Rect
        self.clock_divider_rect: pygame.Rect
        self.board_rect: pygame.Rect

        # -------- Game start -----------------

        self.colour = None
        self.rotation_idx = 0  # 0: white, 1: black: 2: red
        self.game_id = None

        # ------------------------------------

        self.orig_segment_polygons = gen_polygons()
        self.segment_polygons = None

        self.place_elements()
        self.generate_pieces()

        self.highlighted_piece = None

        # Promoting
        self.is_promoting = False
        self.promotion_move = None
        self.promotion_piece = None
        self.promotion_polygons = []
        self.orig_promotion_images = []
        self.promotion_images = []
        self.promotion_pieces = ['q', 'n', 'r', 'b']

    def load_spritesheet(self):
        piece_size = 135
        chess_sprite_image = pygame.image.load('./Assets/chess_pieces.png').convert_alpha()

        piece_letters = ['k', 'q', 'b', 'n', 'r', 'p']
        piece_colours = ['w', 'b', 'r', 'd']
        for col, letter in enumerate(piece_letters):
            for row, colour in enumerate(piece_colours):
                piece_rect = pygame.Rect(col * piece_size, row * piece_size, piece_size, piece_size)
                piece_surface = pygame.Surface((piece_size, piece_size), pygame.SRCALPHA, 32)
                piece_surface.blit(chess_sprite_image, (0, 0), piece_rect)

                self.piece_image_dict[colour + letter] = piece_surface

    def place_elements(self):
        main_height = App.window.get_height() - 2 * SIDE_PADDING

        board_height = main_height - 2 * CLOCK_HEIGHT
        self.board_scale = board_height / self.orig_board_image.get_height()
        board_width = self.orig_board_image.get_width() * self.board_scale
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

        self.segment_polygons = resize_polygons(self.orig_segment_polygons, self.board_scale, self.board_rect.topleft)

        for piece in self.graphical_pieces:
            piece.gen_image(self)

        self.flip_board()

    def generate_pieces(self):
        for segment in range(3):
            for row in range(4):
                for col in range(8):
                    piece_id = self.board.position[segment][row][col]
                    if piece_id is not None:
                        pos = Position(segment, (col, row))
                        image = self.piece_image_dict[piece_id]
                        dead_image = self.piece_image_dict['d' + piece_id[1]]
                        new_piece = GraphicalPiece(piece_id, pos, image, dead_image, self)
                        self.graphical_pieces.append(new_piece)

    def update_dead_pieces(self):
        dead_pieces = self.board.checkmated_players + self.board.stalemated_players
        for piece in self.graphical_pieces:
            if piece.piece_id[0] in dead_pieces:
                piece.dead = True
                piece.image = piece.dead_image
                piece.update_pixel_pos(self)
            else:
                piece.dead = False

    def get_piece_at(self, pos):
        for piece in self.graphical_pieces:
            if piece.pos == pos:
                return piece

    # 0: white, 1: black, 2: red
    def flip_board(self):
        board_image_copy = self.board_image.copy()
        rotation_angle = -120 * self.rotation_idx
        rotated_image = pygame.transform.rotate(board_image_copy, rotation_angle)
        rotated_image_rect = rotated_image.get_rect(center=self.board_rect.center)
        self.board_image = rotated_image
        self.board_rect = rotated_image_rect

        for piece in self.graphical_pieces:
            piece.update_pixel_pos(self)

    def update_piece_move(self, piece, move, is_drop, server_move=False):  # Give GraphicalPiece that moved, drop:
        polygon = shapely.Polygon(self.segment_polygons[(move.end.segment - self.rotation_idx) % 3]
                                  [int(move.end.square.y * 8 + move.end.square.x)])
        end_pixel_pos = polygon.centroid.x, polygon.centroid.y

        # Promotion
        if not move.is_promotion:
            piece.do_move(end_pixel_pos, is_drop)
        else:
            # Create a new piece on the promotion square
            pos = move.end
            piece_id = piece.piece_id[0] + move.promo_type
            image = self.piece_image_dict[piece_id]
            dead_image = self.piece_image_dict['d' + piece_id[1]]
            new_piece = GraphicalPiece(piece_id, pos, image, dead_image, self)
            new_piece.gen_image(self)
            self.graphical_pieces.append(new_piece)

            self.graphical_pieces.remove(piece)  # Remove original piece

        # Capture
        if self.board.index_position(move.end):
            if self.board.index_position(move.end)[0] != piece.piece_id[0]:
                capture_piece = self.get_piece_at(move.end)
                self.graphical_pieces.remove(capture_piece)
        # Castle
        if move.move_type == 'kingside castle' or move.move_type == 'queenside castle':
            if move.move_type == 'kingside castle':
                rook_pos = Position(move.end.segment, (move.end.square.x + 1, move.end.square.y))
                rook_end_pos = Position(rook_pos.segment, (rook_pos.square.x - 2, rook_pos.square.y))
            else:
                rook_pos = Position(move.end.segment, (move.end.square.x - 2, move.end.square.y))
                rook_end_pos = Position(rook_pos.segment, (rook_pos.square.x + 3, rook_pos.square.y))

            rook = self.get_piece_at(rook_pos)
            rook_end_polygon = shapely.Polygon(self.segment_polygons[(rook_end_pos.segment - self.rotation_idx) % 3]
                                               [int(rook_end_pos.square.y * 8 + rook_end_pos.square.x)])
            rook_end_pixel_pos = rook_end_polygon.centroid.x, rook_end_polygon.centroid.y
            rook.do_move(rook_end_pixel_pos, is_drop=is_drop)
            rook.pos = rook_end_pos

        # Enpassant
        if move.move_type == 'enpassant':
            capture_pos = Position(move.end.segment, (move.end.square.x, move.end.square.y - 1))
            capture_piece = self.get_piece_at(capture_pos)
            self.graphical_pieces.remove(capture_piece)

        piece.pos = move.end

        # -------------------- Send move to server ---------------------------
        if not server_move:
            colour = self.board.index_position(move.start)[0]
            move_data = move.gen_json(colour)
            move_data['game id'] = self.game_id
            packet_data = {
                'type': 'move',
                'data': move_data
            }
            packet_json = json.dumps(packet_data)
            App.client.send_packet(packet_json)

    def handle_drag_and_drop(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Dragging if piece is clicked on, and mouse is held down
        # Dropped if mouse is let go, after clicking on piece

        drop = False

        # Highlighted piece detection
        for piece in self.graphical_pieces:
            if App.left_click:
                if piece.rect.collidepoint((mouse_x, mouse_y)):
                    if piece.piece_id[0] == self.board.turn and piece.piece_id[0] == self.colour:
                        piece.moves = piece_movegen(self.board, piece.pos, piece.piece_id[0])
                        self.highlighted_piece = piece

            if piece.is_moving:
                piece.do_animation()

        if self.highlighted_piece:
            if pygame.mouse.get_pressed()[0]:  # Drag
                if not self.highlighted_piece.picked_up:
                    if self.highlighted_piece.rect.collidepoint((mouse_x, mouse_y)):
                        self.highlighted_piece.picked_up = True
                        self.highlighted_piece.image = self.highlighted_piece.selected_image
                        self.highlighted_piece.rect = self.highlighted_piece.image.get_rect(center=(mouse_x, mouse_y))
            else:
                if self.highlighted_piece.picked_up:  # Drop
                    drop = True
                    self.highlighted_piece.picked_up = False
                    # Return to starting position and colour
                    self.highlighted_piece.image = self.highlighted_piece.normal_image
                    self.highlighted_piece.rect = self.highlighted_piece.image.get_rect(
                        center=self.highlighted_piece.original_pixel_pos)

            if self.highlighted_piece.picked_up:
                self.highlighted_piece.rect.center = (mouse_x, mouse_y)  # Move with mouse

            # Click or drop on move square
            for move in self.highlighted_piece.moves:
                polygon_pts = self.segment_polygons[(move.end.segment - self.rotation_idx) % 3][int(move.end.square.y * 8 + move.end.square.x)]
                polygon = shapely.Polygon(polygon_pts)

                mouse_pos = shapely.Point(pygame.mouse.get_pos())
                if polygon.contains(mouse_pos):
                    if App.left_click or drop:  # Make the move
                        if not move.is_promotion:
                            self.update_piece_move(self.highlighted_piece, move, drop)
                            self.board.make_move(move)
                            self.update_dead_pieces()
                        else:  # User must select what type of promotion
                            self.is_promoting = True
                            self.promotion_move = move
                            # Calculate promotion stuff
                            for row in range(4):
                                # Polygon
                                polygon_pts = self.segment_polygons[(move.end.segment + self.rotation_idx) % 3][int((move.end.square.y - row) * 8 + move.end.square.x)]
                                self.promotion_polygons.append(polygon_pts)
                                # Image
                                piece_type = self.promotion_pieces[row]
                                piece_orig_image = self.piece_image_dict[self.colour + piece_type]
                                piece_image = pygame.transform.smoothscale(piece_orig_image,
                                    (0.07 * self.board_image.get_height(), 0.07 * self.board_image.get_height())
                                )
                                self.orig_promotion_images.append(piece_orig_image)
                                self.promotion_images.append(piece_image)

                                self.promotion_piece = self.highlighted_piece
                        self.highlighted_piece = None


    def resize(self, new_size):
        self.place_elements()

    def update(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if not self.is_promoting:
            self.handle_drag_and_drop()
        else:
            mouse_point = shapely.Point((mouse_x, mouse_y))
            for i, polygon_pts in enumerate(self.promotion_polygons):
                polygon = shapely.Polygon(polygon_pts)
                if App.left_click:
                    if polygon.contains(mouse_point):
                        promo_piece = self.promotion_pieces[i]
                        self.promotion_move.promo_type = promo_piece

                        self.update_piece_move(self.promotion_piece, self.promotion_move, True)
                        self.board.make_move(self.promotion_move)
                        self.update_dead_pieces()
                        # Reset promotion stuff
                        self.is_promoting = False
                        self.promotion_move = None
                        self.promotion_piece = None
                        self.promotion_polygons = []
                        self.orig_promotion_images = []
                        self.promotion_images = []

                        break

        if App.client.last_message:
            if App.client.last_message['type'] == 'game start':
                self.colour = App.client.last_message['data']['colours'][App.client.username]
                self.rotation_idx = self.board.turns.index(self.colour)
                print(self.colour, self.rotation_idx)

                self.game_id = App.client.last_message['data']['game id']

                self.flip_board()
            if App.client.last_message['type'] == 'move':
                move_obj = json_to_move_obj(App.client.last_message['data'])
                print(move_obj.start)
                target_piece = None
                for piece in self.graphical_pieces:
                    if piece.pos == move_obj.start:
                        target_piece = piece
                self.update_piece_move(target_piece, move_obj, is_drop=False, server_move=True)
                self.board.make_move(move_obj)
                self.update_dead_pieces()
            App.client.last_message = None

        self.draw()

    def draw(self):
        App.window.fill((250, 245, 240))

        pygame.draw.rect(App.window, (227, 228, 224), self.move_divider_rect)
        App.window.blit(self.board_image, self.board_rect)

        for piece in self.graphical_pieces:
            if piece != self.highlighted_piece:  # For ordering
                App.window.blit(piece.image, piece.rect)
            else:
                if piece.picked_up:
                    App.window.blit(piece.ghost_image, piece.ghost_rect)

        if self.highlighted_piece:
            for move in self.highlighted_piece.moves:
                polygon_pts = self.segment_polygons[(move.end.segment - self.rotation_idx) % 3][int(move.end.square.y * 8 + move.end.square.x)]
                polygon = shapely.Polygon(polygon_pts)
                centre_x, centre_y = polygon.centroid.x, polygon.centroid.y

                pygame.draw.circle(App.window, (255, 0, 0), (centre_x, centre_y), 10)

                mouse_pos = shapely.Point(pygame.mouse.get_pos())
                if polygon.contains(mouse_pos):
                    pygame.draw.polygon(App.window, (255, 255, 255), polygon_pts, width=2)

            App.window.blit(self.highlighted_piece.image, self.highlighted_piece.rect)

        if self.is_promoting:
            for row in range(4):
                image = self.promotion_images[row]
                polygon_pts = self.promotion_polygons[row]
                polygon = shapely.Polygon(polygon_pts)
                image_center = polygon.centroid.x, polygon.centroid.y
                rect = image.get_rect(center=image_center)

                pygame.draw.polygon(App.window, (255, 255, 255), polygon_pts)
                App.window.blit(image, rect)

