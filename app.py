import pygame
import pygame.freetype


class App:
    pygame.init()
    pygame.display.set_caption('3 Player Chess')

    w_width, w_height = (960, 590)
    window = pygame.display.set_mode((960, 590), pygame.RESIZABLE)

    left_click = False

    _done = False
    _clock = pygame.time.Clock()
    _state_dict = None
    _current_state = None

    @staticmethod
    def init_states(state_dict, start_state_name):
        App._state_dict = state_dict
        App._current_state = App._state_dict[start_state_name]

    @staticmethod
    def resize(new_size):
        for state in App._state_dict.values():
            state.resize(new_size)

    @staticmethod
    def flip_state():
        App._current_state = App._state_dict[App._current_state.next]

    @staticmethod
    def update():
        if App._current_state.done:
            App.flip_state()
        App._current_state.update()

    @staticmethod
    def event_loop():
        App.left_click = False
        for event in pygame.event.get(pump=True):
            App._current_state.get_event(event)
            if event.type == pygame.QUIT:
                App._done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                App.left_click = True
            if event.type == pygame.VIDEORESIZE:
                if event.size[0] / event.size[1] >= 1.2 and event.size[0] >= 852 and event.size[1] >= 480:
                    App.w_width, App.w_height = event.size
                    App.resize(event.size)
                else:
                    App.window = pygame.display.set_mode((App.w_width, App.w_height), pygame.RESIZABLE)

    @staticmethod
    def loop():
        while not App._done:
            App._clock.tick(60)
            App.event_loop()

            App.update()

            pygame.display.update()

        pygame.quit()
