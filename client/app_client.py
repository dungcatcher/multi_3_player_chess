import socket
import asyncio

HOST = "localhost"
PORT = 65432


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


async def connect_to_server():
    with client_socket as s:
        s.connect((HOST, PORT))
        s.sendall(b'Hello World')
        print('connected')

asyncio.create_task(connect_to_server())
