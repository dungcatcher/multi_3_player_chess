import socket
import asyncio

HOST = "localhost"
PORT = 65432


class Client:
    def __init__(self):
        self.connection_loop = asyncio.get_event_loop()
        task = self.connection_loop.create_task(self.connect_to_server())
        self.connection_loop.run_until_complete(task)

    def start(self):
        pass

    async def connect_to_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(b'Hello world')