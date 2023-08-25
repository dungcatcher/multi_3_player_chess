import socket
import threading
import json

HOST = "oggyp.com"
PORT = 65432


class AppClient:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.last_message = None
        self.pending_message = None

        self.logged_in = False
        self.username = None

        connect_thread = threading.Thread(target=self.connect_to_server, daemon=True)
        connect_thread.start()

    def send_packet(self, packet):
        self.socket.sendall(packet.encode())

    def connect_to_server(self):
        try:
            self.socket.connect((HOST, PORT))
            print('connected')
            self.connected = True
            listen_thread = threading.Thread(target=self.listen, daemon=True)
            listen_thread.start()
        except socket.error:
            print('connection failed')

    def listen(self):
        with self.socket as s:
            while True:
                data = s.recv(1024)
                if not data:
                    break
                decoded_data = data.decode()
                data_dict = json.loads(decoded_data)
                # Client hasn't finished processing last message
                if not self.last_message:
                    self.last_message = data_dict
                else:
                    self.pending_message = data_dict
                    while True:
                        if not self.last_message:
                            self.last_message = self.pending_message
                            break

