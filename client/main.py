from client.app import App
from client.States.Menu.menu import Menu
from client.States.Game.game import Game
from client.States.Lobby.lobby import Lobby
from client.States.Login.login import Login
from client.States.Analysis.analysis import Analysis

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
        'analysis': Analysis(),
        'game': Game(),
        'lobby': Lobby(),
        'login': Login()
    }
    App.init_states(state_dict, 'login')
    App.loop()


main()
