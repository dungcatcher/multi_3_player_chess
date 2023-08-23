from ...widget import Label
import time
from client.app import App


class Clock:
    def __init__(self, rect, start_time):
        self.rect = rect
        self.clock_time = start_time
        self.is_ticking = False

        self.previous_time = None

        self.label = Label(self.rect.left, self.rect.top, self.rect.width, self.rect.height, self.gen_time_string(), 'topleft',
                           (255, 255, 255), None, (0, 0, 0), align='center')

    def place_elements(self):
        self.label = Label(self.rect.left, self.rect.top, self.rect.width, self.rect.height, self.gen_time_string(),
                           'topleft',
                           (255, 255, 255), None, (0, 0, 0), align='center')

    def gen_time_string(self):
        if self.clock_time >= 10:
            rounded_time = round(self.clock_time)
        else:
            rounded_time = round(self.clock_time, 2)

        minutes = str(rounded_time // 60)
        if len(minutes) == 1:
            minutes = '0' + minutes

        seconds = str(rounded_time % 60)
        if len(seconds) == 1:
            seconds = '0' + seconds

        if self.clock_time <= 0:
            return '00:00'

        output = f'{minutes}:{seconds}'
        return output

    def update(self):
        if self.is_ticking:
            if not self.previous_time:
                self.previous_time = time.time()

            delta_time = time.time() - self.previous_time
            self.clock_time -= delta_time

            self.label.label = self.gen_time_string()

            self.previous_time = time.time()

    def draw(self):
        self.label.draw(App.window)


