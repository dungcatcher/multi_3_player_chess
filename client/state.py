class State:
    def __init__(self):
        self.done = False
        self.next = None  # Next state (on button press or something)
        self.quit = False  # Exit the app

    def get_event(self, event):
        pass

    def resize(self, new_size):
        pass

    def update(self):
        pass

    def draw(self):
        pass

    def reset(self):
        pass
