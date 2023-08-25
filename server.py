import socket
import threading
import json
import random
import string
import time
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
        print(game.player_data)
        for player_name, data in game.player_data.items():
            player_colours[player_name] = data['colour']
        server_times = {}
        for player_name, data in game.player_data.items():
            server_times[data['colour']] = data['time']

        packet = {
            'colours': player_colours,
            'game id': game_id,
            'times': server_times
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
            already_in_game = False
            # Not already in a game
            for game in self.games.values():
                for player in game.player_data.values():
                    if conn == player['socket']:
                        already_in_game = True
            if response_dict['data'] == 'new':  # New game created
                if not already_in_game:
                    game_id = ''.join(random.choice(string.digits + string.ascii_letters) for _ in range(10))  # Random game id
                    new_game = Game()
                    new_game.add_player(username, conn)
                    self.games[game_id] = new_game

            elif response_dict['data'] != 'init':  # Joined existing game
                target_game_id = response_dict['data']
                if not self.games[target_game_id].started:
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

            server_times = {}
            for username, player in self.games[game_id].player_data.items():
                server_times[player['colour']] = player['time']
            response_dict['data']['times'] = server_times  # Use servers values for times instead of clients

            move_packet = {
                'type': 'move',
                'data': response_dict['data']
            }
            for player in self.games[game_id].player_data.values():
                player_conn = player['socket']
                if conn != player_conn:  # Don't send back to person who sent the move
                    send_response(player_conn, move_packet)
                else:
                    timer_packet = {
                        'type': 'timer',
                        'data': server_times
                    }
                    send_response(conn, timer_packet)

            move_obj = json_to_move_obj(response_dict['data'])
            self.games[game_id].board.make_move(move_obj)

            self.games[game_id].board.check_winner()
            if self.games[game_id].board.terminated:  # Game over
                termination_data = {
                    'termination type': self.games[game_id].board.termination_type,
                    'results': self.games[game_id].board.results
                }
                termination_packet = {
                    'type': 'termination',
                    'data': termination_data
                }
                for username, data in self.games[game_id].player_data.items():
                    send_response(data['socket'], termination_packet)

            if not self.games[game_id].start_timer:  # First move of the game
                self.games[game_id].start_timer = True
                self.games[game_id].previous_time = time.time()
            for username, player in self.games[game_id].player_data.items():  # Update user time
                if player['colour'] == self.games[game_id].board.turn:
                    self.games[game_id].turn = username

    def remove_socket(self, conn):
        # Remove from lobby
        if conn in self.in_lobby:
            self.in_lobby.remove(conn)
        # Remove from logged in
        for username, user_sock in self.logged_in.items():
            if conn == user_sock:
                del self.logged_in[username]
                break
        # Remove from game
        for game in self.games.values():
            for username, data in game.player_data.items():
                if conn == data['socket']:  # Player is in game, handle closing
                    player_colour = game.player_data[username]['colour']
                    if not game.started:
                        game.available_colours.append(player_colour)
                        del game.player_data[username]

                        # Send updated queue data to all users
                        game_json_list = [self.gen_lobby_game_packet_data(game_id) for game_id in self.games.keys()]
                        game_packet = {
                            'type': 'queue',
                            'data': game_json_list
                        }
                        # Update all users in lobby
                        for user_conn in self.in_lobby:
                            send_response(user_conn, game_packet)

                        break
                    else:  # Game has started
                        game.board.disconnected_players.append(player_colour)
                        if player_colour in game.board.stalemated_players:
                            game.board.stalemated_players.remove(player_colour)

                        game.board.check_winner()
                        if game.board.terminated:  # Leaving resulted in someone winning
                            game.board.termination_type = 'abandoned'

                            termination_data = {
                                'termination type': game.board.termination_type,
                                'results': game.board.results
                            }
                            termination_packet = {
                                'type': 'termination',
                                'data': termination_data
                            }

                            for term_username, term_data in game.player_data.items():
                                if term_data['colour'] != player_colour:
                                    send_response(term_data['socket'], termination_packet)

                        # Skip the players turn if it is their turn
                        if game.board.turn == player_colour:
                            game.board.turn_index = (game.board.turn_index + 1) % len(game.board.turns)
                            game.board.turn = game.board.turns[game.board.turn_index]

                            for turn_username, turn_data in game.player_data.items():
                                if turn_data['colour'] == game.board.turn:
                                    game.turn = turn_username

                        del game.player_data[username]  # Delete from player list

                        # Send disconnection packet to all clients
                        disconnect_data = {
                            'turn index': game.board.turn_index,
                            'stalemated': game.board.stalemated_players,
                            'disconnected': game.board.disconnected_players,
                        }
                        disconnect_packet = {
                            'type': 'disconnect',
                            'data': disconnect_data
                        }
                        for other_usernames, user_data in game.player_data.items():
                            send_response(user_data['socket'], disconnect_packet)

                        break

        conn.close()

    def client_handler(self, conn, addr):
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                self.handle_response(conn, addr, data)
            except ConnectionResetError:
                self.remove_socket(conn)
                break

    def game_handler(self):
        while True:
            for game in self.games.values():
                if game.started:
                    game.update()

    def loop(self):
        game_handler_thread = threading.Thread(target=self.game_handler, args=(), daemon=True)
        game_handler_thread.start()

        with self.socket as s:
            s.listen()
            while True:
                conn, addr = s.accept()
                print(f'{addr} has connected!')
                client_thread = threading.Thread(target=self.client_handler, args=(conn, addr), daemon=True)
                client_thread.start()


server = Server()
server.loop()
