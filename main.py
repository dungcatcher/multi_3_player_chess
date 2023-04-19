from app import App
from States.Menu.menu import Menu
from States.Game.game import Game
from States.Lobby.lobby import Lobby


def main():
    state_dict = {
        'menu': Menu(),
        'game': Game(),
        'lobby': Lobby()
    }
    App.init_states(state_dict, 'menu')
    App.loop()


main()
