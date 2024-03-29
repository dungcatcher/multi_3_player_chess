from chesslogic.movegen import piece_movegen, make_move, colour_to_segment, get_game_state
from chesslogic.classes import Position

STARTING_POSITION = [
    [  # White segment
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
        ["wr", "wn", "wb", 'wq', "wk", "wb", "wn", "wr"]
    ],
    [  # Black segment
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
        ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"]
    ],
    [  # Red segment
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        ["rp", "rp", "rp", "rp", "rp", "rp", "rp", "rp"],
        ["rr", "rn", "rb", "rq", "rk", "rb", "rn", "rr"]
    ]
]


letter_to_colour = {
    'w': 'white',
    'b': 'black',
    'r': 'red'
}


def test_fastest_checkmate(board, depth):
    moves = 0
    turn_legal_moves = []
    for segment in range(3):
        for y in range(4):
            for x in range(8):
                square_occupant = board.position[segment][y][x]
                if square_occupant is not None and square_occupant[0] == board.turn:
                    turn_legal_moves += piece_movegen(board, Position(segment, (x, y)), square_occupant[0])

    if depth == 0:
        return len(turn_legal_moves)

    for move in turn_legal_moves:
        new_board = make_move(board, move)
        new_board.turn_index = (new_board.turn_index + 1) % len(new_board.turns)
        new_board.turn = new_board.turns[new_board.turn_index]
        moves += test_fastest_checkmate(new_board, depth - 1)

    return moves


class Board:
    def __init__(self):
        """
        Board is represented as a list of 2d arrays of the 3 8x4 segments
        """
        self.position = STARTING_POSITION
        self.turns = ["w", "b", "r"]
        self.turn_index = 0
        self.turn = self.turns[self.turn_index]
        self.stalemated_players = []
        self.checkmated_players = []
        self.disconnected_players = []
        self.castling_rights = {
            'w': {'kingside': True, 'queenside': True},
            'b': {'kingside': True, 'queenside': True},
            'r': {'kingside': True, 'queenside': True}
        }
        self.enpassant_squares = {  # Squares that can be taken en passant
            'w': None, 'b': None, 'r': None
        }

        self.skipped_turn = None

        self.terminated = False
        self.results = {'w': 0, 'b': 0, 'r': 0}
        self.termination_type = None

    def index_position(self, position):  # Helper function to prevent long indexing code
        return self.position[int(position.segment)][int(position.square.y)][int(position.square.x)]

    def update_castling_rights(self, move):
        piece_colour = self.index_position(move.end)[0]
        king_square = self.index_position(Position(colour_to_segment[piece_colour], (4, 3)))
        if king_square != f'{piece_colour}k':  # If the king is not on its start square it has moved
            self.castling_rights[piece_colour]["queenside"] = False
            self.castling_rights[piece_colour]["kingside"] = False
        kingside_rook_square = self.index_position(Position(colour_to_segment[piece_colour], (7, 3)))
        if kingside_rook_square is None or kingside_rook_square != f'{piece_colour}r':
            self.castling_rights[piece_colour]["kingside"] = False
        queenside_rook_square = self.index_position(Position(colour_to_segment[piece_colour], (0, 3)))
        if queenside_rook_square is None or queenside_rook_square != f'{piece_colour}r':
            self.castling_rights[piece_colour]["queenside"] = False

    def check_winner(self):
        # Check if the next player is in checkmate or stalemate
        latest_result = None

        self.stalemated_players = []
        for turn in self.turns:
            if turn not in self.disconnected_players and turn not in self.checkmated_players:
                game_state = get_game_state(self, turn)
                if game_state == 'stalemate':
                    latest_result = 'stalemate'
                    self.stalemated_players.append(turn)
                if game_state == 'checkmate':
                    latest_result = 'checkmate'
                    self.checkmated_players.append(turn)

        if latest_result == 'checkmate':
            print(self.checkmated_players, self.disconnected_players)
            if len(self.checkmated_players + self.disconnected_players) == 2:
                self.terminated = True
                for turn in self.turns:
                    if turn not in self.checkmated_players + self.disconnected_players:
                        self.results[turn] = 1
                        self.termination_type = 'checkmate'
        if latest_result == 'stalemate':
            if len(self.checkmated_players + self.disconnected_players + self.stalemated_players) == 2:
                self.terminated = True
                for turn in self.turns:
                    if turn not in self.checkmated_players + self.disconnected_players:
                        self.results[turn] = 0.5
                        self.termination_type = 'stalemate'
        if len(self.disconnected_players) == 2:
            self.terminated = True
            for turn in self.turns:
                if turn not in self.disconnected_players:
                    self.results[turn] = 1
                    self.termination_type = 'abandoned'
        # if len(self.checkmated_players) == 2:  # Both other players are in checkmate
        #     self.terminated = True
        #     for turn in self.turns:
        #         if turn not in self.checkmated_players:
        #             self.results[turn] = 1  # Winner is the person not in checkmate
        #             self.termination_type = 'checkmate'
        # if len(self.checkmated_players + self.stalemated_players) == 2:  # Other player is in stalemate -> draw
        #     self.terminated = True
        #     for turn in self.turns:
        #         if turn not in self.checkmated_players:
        #             self.results[turn] = 0.5
        #             self.termination_type = 'stalemate'

    def make_move(self, move):
        move_colour = self.index_position(move.start)[0]

        self.position = make_move(self, move).position
        self.update_castling_rights(move)
        self.enpassant_squares[move_colour] = None
        if move.move_type == "double push":
            self.enpassant_squares[move_colour] = Position(move.end.segment, (move.end.square.x, move.end.square.y + 1))

        self.turn_index = (self.turn_index + 1) % len(self.turns)
        self.turn = self.turns[self.turn_index]

        """
        Everytime a move is a made, check for players in stalemate add to list (clear first)
        Also check for players in checkmate, add to list
        Skip turn if they are in checkmate or stalemate
        """

        self.check_winner()

        self.skipped_turn = None
        # Skip turn
        skip_turn = self.stalemated_players + self.checkmated_players + self.disconnected_players
        if self.turn in skip_turn:
            self.skipped_turn = self.turn

            self.turn_index = (self.turn_index + 1) % len(self.turns)
            self.turn = self.turns[self.turn_index]
