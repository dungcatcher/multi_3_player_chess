from app import App
from States.Menu.menu import Menu
from States.Game.game import Game
from States.Lobby.lobby import Lobby

"""
Moving to client and server folders:

chess logic:
    board.py
    movegen.py
    classes.py

server:
    main.py
    
client:
    main.py
    app.py
    state.py
    widget.py
    states:
        game:
            game.py
            graphical_piece.py
            polygon.py
        lobby: ...
        menu: ...
    
"""


def main():
    state_dict = {
        'menu': Menu(),
        'game': Game(),
        'lobby': Lobby()
    }
    App.init_states(state_dict, 'menu')
    App.loop()


main()
