import socket
import threading
import json
import random
import string
from server.game import Game
from chesslogic.classes import json_to_move_obj

HOST = "localhost"
PORT = 65432


def send_response(conn, response):
    response_packet = json.dumps(response).encode()
    conn.sendall(response_packet)


class Server:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT))
        with open('data/users.json') as f:
            self.users = json.load(f)

        self.addresses = {}
        self.in_lobby = []

        self.logged_in = {}  # username: socket

        self.games = {}

    # Viewing games going on in the lobby
    def gen_lobby_game_packet_data(self, game_id):
        player_names = list(self.games[game_id].player_data)
        data = {
            'id': game_id,
            'players': player_names
        }
        return data

    # Actual game
    def gen_game_packet_data(self, game_id):
        game = self.games[game_id]
        player_colours = {}
        for player_name, data in game.player_data.items():
            player_colours[player_name] = data['colour']

        packet = {
            'colours': player_colours,
            'game id': game_id
        }

        return packet

    def get_username(self, target_socket):
        target_username = None
        for username, user_socket in self.logged_in.items():
            if target_socket == user_socket:
                target_username = username
        return target_username

    def handle_response(self, conn, addr, response):
        decoded = response.decode()
        response_dict = json.loads(decoded)

        # ----- Login -----
        if response_dict['type'] == 'login':
            login_data = json.loads(response_dict['data'])
            if login_data['username'] not in self.users.keys():  # Account doesn't exist, error
                response_data = {'type': 'login', 'data': 'not found'}
                send_response(conn, response_data)
            else:
                if login_data['password'] == self.users[login_data['username']]['password']:  # Password is correct
                    if login_data['username'] not in self.logged_in.keys():
                        self.logged_in[login_data['username']] = conn
                        response_data = {'type': 'login', 'data': 'logged in'}
                        send_response(conn, response_data)
                    else:
                        print('Already logged in')
                else:
                    response_data = {'type': 'login', 'data': 'incorrect password'}
                    send_response(conn, response_data)

        # ----- Register -----
        if response_dict['type'] == 'register':
            register_data = json.loads(response_dict['data'])
            if register_data['username'] not in self.users.keys():  # Account doesn't exist, good
                self.users[register_data['username']] = {'password': register_data['password']}
                with open('data/users.json', 'w') as f:
                    json.dump(self.users, f)
                response_data = {'type': 'register', 'data': 'created'}
                send_response(conn, response_data)
            else:  # Account already exists, error
                response_data = {'type': 'register', 'data': 'already exists'}
                send_response(conn, response_data)

        # ----- Queue -----
        if response_dict['type'] == 'queue':
            username = self.get_username(conn)
            if response_dict['data'] == 'new':  # New game created
                game_id = ''.join(random.choice(string.digits + string.ascii_letters) for _ in range(10))  # Random game id
                new_game = Game()
                new_game.add_player(username, conn)
                self.games[game_id] = new_game
            elif response_dict['data'] != 'init':  # Joined existing game
                target_game_id = response_dict['data']
                if not self.games[target_game_id].started:
                    already_in_game = False
                    # Not already in a game
                    for game in self.games.values():
                        if conn in game.player_data:
                            already_in_game = True
                    if not already_in_game:
                        self.games[target_game_id].add_player(username, conn)
                        # Check to see if the game has started
                        if self.games[target_game_id].started:
                            # All users need board data, players and their colours,
                            response_data = self.gen_game_packet_data(target_game_id)
                            response_packet = {'type': 'game start', 'data': response_data}
                            for player in self.games[target_game_id].player_data.values():
                                player_conn = player['socket']
                                print(player_conn)
                                send_response(player_conn, response_packet)
                                self.in_lobby.remove(player_conn)
                    else:
                        print('Already in game')
                else:
                    print('Game is full')
            elif response_dict['data'] == 'init':
                self.in_lobby.append(conn)
            # Includes init
            game_json_list = [self.gen_lobby_game_packet_data(game_id) for game_id in self.games.keys()]
            game_packet = {
                'type': 'queue',
                'data': game_json_list
            }
            # Update all users in lobby
            for user_conn in self.in_lobby:
                send_response(user_conn, game_packet)

        # --------- In game ---------------------
        if response_dict['type'] == 'move':
            game_id = response_dict['data']['game id']
            move_packet = {
                'type': 'move',
                'data': response_dict['data']
            }
            for player in self.games[game_id].player_data.values():
                player_conn = player['socket']
                if conn != player_conn:  # Don't send back to person who sent the move
                    send_response(player_conn, move_packet)

            move_obj = json_to_move_obj(response_dict['data'])
            self.games[game_id].board.make_move(move_obj)

    def client_handler(self, conn, addr):
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                self.handle_response(conn, addr, data)

    def loop(self):
        with self.socket as s:
            s.listen()
            while True:
                conn, addr = s.accept()
                print(f'{addr} has connected!')
                self.addresses[str(addr)] = conn
                client_thread = threading.Thread(target=self.client_handler, args=(conn, addr), daemon=True)
                client_thread.start()


server = Server()
server.loop()