import json
from client.app import App
from client.widget import Button
from client.state import State


class Menu(State):
    def __init__(self):
        super().__init__()
        self.analysis_button = Button(100, 100, 200, 50, 'Analysis', 'topleft')
        self.play_button = Button(100, 200, 200, 50, 'Play', 'topleft')

    def update(self):
        if not App.client.logged_in:
            self.play_button.disabled = True

        self.analysis_button.update()
        self.play_button.update()

        if App.left_click:
            if self.analysis_button.hovered:
                self.done = True
                self.next = 'analysis'

        if App.left_click:
            if self.play_button.hovered:
                self.done = True
                self.next = 'lobby'

                # Request queue data
                request_data = {
                    'type': 'queue',
                    'data': 'init'
                }
                request_packet = json.dumps(request_data)
                App.client.send_packet(request_packet)
                print(request_packet)

        self.draw()

    def draw(self):
        App.window.fill((250, 245, 240))
        self.analysis_button.draw()
        self.play_button.draw()

