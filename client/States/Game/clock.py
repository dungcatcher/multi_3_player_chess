from ...widget import Label
import time


class Clock:
    def __init__(self, rect, start_time):
        self.rect = rect
        self.time = start_time
        self.is_ticking = False

    def update(self):
        if self.is_ticking:
            pass


