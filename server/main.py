import socket
import threading
import json

HOST = "localhost"
PORT = 65432


class Server:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT))
        with open('users.json') as f:
            self.users = json.load(f)

    def handle_response(self, response):
        decoded = response.decode()
        response_dict = json.loads(decoded)
        if response_dict['type'] == 'login':
            login_data = json.loads(response_dict['data'])
        if response_dict['type'] == 'register':
            register_data = json.loads(response_dict['data'])
            if register_data['username'] not in self.users.keys():
                self.users[register_data['username']] = {'password': register_data['password']}
                with open('users.json', 'w') as f:
                    json.dump(self.users, f)
            else:
                print('already exists')

    def client_handler(self, conn, addr):
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                self.handle_response(data)

    def loop(self):
        with self.socket as s:
            s.listen()
            while True:
                conn, addr = s.accept()
                print(f'{addr} has connected!')
                client_thread = threading.Thread(target=self.client_handler, args=(conn, addr), daemon=True)
                client_thread.start()


server = Server()
server.loop()