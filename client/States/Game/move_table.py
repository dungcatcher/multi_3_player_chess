COORDINATE_TABLE = [
    [  # White
        ['a4', 'b4', 'c4', 'd4', 'e4', 'f4', 'g4', 'h4'],
        ['a3', 'b3', 'c3', 'd3', 'e3', 'f3', 'g3', 'h3'],
        ['a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2'],
        ['a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1'],
    ],
    [  # Black
        ['h9', 'g9', 'f9', 'e9', 'i9', 'j9', 'k9', 'l9'],
        ['h10', 'g10', 'f10', 'e10', 'i10', 'j10', 'k10', 'l10'],
        ['h11', 'g11', 'f11', 'e11', 'i11', 'j11', 'k11', 'l11'],
        ['h12', 'g12', 'f12', 'e12', 'i12', 'j12', 'k12', 'l12'],
    ],
    [  # Red
        ['l5', 'k5', 'j5', 'i5', 'd5', 'c5', 'b5', 'a5'],
        ['h5', 'g5', 'f5', 'e5', 'i5', 'j5', 'k5', 'l5'],
        ['h4', 'g4', 'f4', 'e4', 'i4', 'j4', 'k4', 'l4'],
        ['h3', 'g3', 'f3', 'e3', 'i3', 'j3', 'k3', 'l3'],
    ]
]


# Called before board is updated
def get_move_notation(board, move):
    notation = ''

    piece_id = board.index_position(move.start)

    capture = False
    if board.index_position(move.end):
        capture = True
    end_square = COORDINATE_TABLE[move.end.segment][int(move.end.square.y)][int(move.end.square.x)]

    if piece_id[1] != 'p':
        notation += piece_id[1].upper()
    if capture:
        if piece_id[1] == 'p':
            notation += COORDINATE_TABLE[move.start.segment][int(move.start.square.y)][int(move.start.square.x)][0]
        notation += 'x'
    notation += end_square

    return notation
