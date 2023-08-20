from pygame import Vector2


class Position:
    def __init__(self, segment, square):
        self.segment = segment
        self.square = Vector2(square)

    def __eq__(self, other):
        return self.segment == other.segment and self.square == other.square


class Move:
    def __init__(self, start, end, move_type="normal", is_promotion=False, promo_type=None):
        self.start = start
        self.end = end
        self.move_type = move_type
        self.is_promotion = is_promotion
        self.promo_type = promo_type

    def gen_json(self, colour):
        data = {
            'colour': colour,
            'start': {
                'segment': self.start.segment,
                'square': (self.start.square.x, self.start.square.y)
            },
            'end': {
                'segment': self.end.segment,
                'square': (self.end.square.x, self.end.square.y)
            },
            'move type': self.move_type,
            'is promotion': self.is_promotion,
            'promo type': self.promo_type,
        }

        return data


def json_to_move_obj(move_data):
    start = Position(move_data['start']['segment'], move_data['start']['square'])
    end = Position(move_data['end']['segment'], move_data['end']['square'])

    move_obj = Move(start, end, move_data['move type'], move_data['is promotion'], move_data['promo type'])

    return move_obj
