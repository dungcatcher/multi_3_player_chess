import socket
import threading

HOST = "localhost"
PORT = 65432


class Server:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT))

    def client_handler(self, conn, addr):
        while True:
            pass

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