import socket
import threading
import json

HOST = "localhost"
PORT = 65432


class AppClient:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.last_message = None

        self.logged_in = False
        self.username = None

        connect_thread = threading.Thread(target=self.connect_to_server, daemon=True)
        connect_thread.start()

    def send_packet(self, packet):
        self.socket.sendall(packet.encode())

    def connect_to_server(self):
        self.socket.connect((HOST, PORT))
        print('connected')
        self.connected = True
        listen_thread = threading.Thread(target=self.listen, daemon=True)
        listen_thread.start()

    def listen(self):
        with self.socket as s:
            while True:
                data = s.recv(1024)
                if not data:
                    break
                decoded_data = data.decode()
                data_dict = json.loads(decoded_data)
                self.last_message = data_dict
