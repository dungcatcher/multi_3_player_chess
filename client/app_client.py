import socket
import threading

HOST = "localhost"
PORT = 65432


class AppClient:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        connect_thread = threading.Thread(target=self.connect_to_server, daemon=True)
        connect_thread.start()

    def connect_to_server(self):
        self.socket.connect((HOST, PORT))
        print('connected')
        self.connected = True
        self.socket.sendall(b'Hello World')

