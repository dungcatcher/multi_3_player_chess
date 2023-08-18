import socket
import threading
import json
import random
import string
import pickle
import codecs
from server.game import Game

HOST = "localhost"
PORT = 65432


def send_response(conn, response):
    response_packet = json.dumps(response).encode()
    conn.sendall(response_packet)


class Server:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT))
        with open('users.json') as f:
            self.users = json.load(f)

        self.addresses = {}

        self.games = {}

    def gen_game_packet_data(self, game_id):
        game = self.games[game_id]
        # Use player names
        data = {
            'id': game_id,
            'players': game.players
        }
        return data

    def handle_response(self, conn, addr, response):
        decoded = response.decode()
        response_dict = json.loads(decoded)
        if response_dict['type'] == 'login':
            login_data = json.loads(response_dict['data'])
            if login_data['username'] not in self.users.keys():  # Account doesn't exist, error
                response_data = {'type': 'login', 'data': 'not found'}
                send_response(conn, response_data)
            else:
                if login_data['password'] == self.users[login_data['username']]['password']:  # Password is correct
                    response_data = {'type': 'login', 'data': 'logged in'}
                    send_response(conn, response_data)
                else:
                    response_data = {'type': 'login', 'data': 'incorrect password'}
                    send_response(conn, response_data)
        if response_dict['type'] == 'register':
            register_data = json.loads(response_dict['data'])
            if register_data['username'] not in self.users.keys():  # Account doesn't exist, good
                self.users[register_data['username']] = {'password': register_data['password']}
                with open('users.json', 'w') as f:
                    json.dump(self.users, f)
                response_data = {'type': 'register', 'data': 'created'}
                send_response(conn, response_data)
            else:  # Account already exists, error
                response_data = {'type': 'register', 'data': 'already exists'}
                send_response(conn, response_data)

        if response_dict['type'] == 'queue':
            if response_dict['data'] == 'new':
                game_id = ''.join(random.choice(string.digits + string.ascii_letters) for _ in range(10))  # Random game id
                new_game = Game()
                new_game.add_player(addr)
                self.games[game_id] = new_game
                # Send all games to client
                game_json_list = [self.gen_game_packet_data(game_id) for game_id in self.games.keys()]
                game_packet = {
                    'type': 'queue',
                    'data': game_json_list
                }
                send_response(conn, game_packet)

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