import socket, tkinter as tk, time
from tkinter import ttk
from threading import Thread, main_thread

class socket_client:
    def __init__(self, tp, buffer_size = 120, id = "N/A"):
        self.conn = tp[0]
        self.address = tp[1]
        self.data_archive = []
        self.oldlen = 1
        self.newlen = 0
        self.buffer_size = buffer_size
        if id == "N/A": self.name = tp[1][0]
        else: self.name = id

def connect_server(server, host = socket_client(["127.0.0.1", "65432"]), timeout = 1):
    server.settimeout(timeout)
    try:
        server.connect((host.address, host.port))
        receive_data(host)
        if host.data_archive[-1] == b"NAME?":
            server.sendall(str.encode("Local PC - Tester"))
    except TimeoutError:
        print("Timeout")

def send_data(client, data):
    try:
        sent = client.conn.sendall(str.encode(data))
        time.sleep(0.1)
    except:
        time.sleep(0.1)
        return()

def receive_data(client):
    try:
        data = client.conn.recv(4096)
        if data != b"":
            data = str(data)[2:-1]
            client.data_archive.append(str(data))
            client.conn.sendall(str.encode("Received {} from {}".format(data, client.name)))
        time.sleep(0.1)
    except:
        return()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket_host("127.0.0.1", "65432")
    connect_server(server, host)
    shutdown_client = False
    while shutdown_client == False:
        data = str(input("Qual dado enviar?\n"))
        send_data(server, data)
        if data.casefold() == "shutdown" or data.casefold() == "disconnect": shutdown_client = True


main()

# HOST = "127.0.0.1"  # The server's hostname or IP address
# PORT = 65432  # The port used by the server

# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.connect((HOST, PORT))
#     s.sendall(b"Hello, world")
#     time_start = time.time()
#     time_end = time.time()
#     time_elapsed = time_end - time_start
#     while time_elapsed < 1:
#         data = s.recv(1024)
#         s.sendall(b"Received data")
#         time_end = time.time()
#         time_elapsed = time_end - time_start

# print(f"Received {data!r}")