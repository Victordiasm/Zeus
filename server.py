import socket, tkinter as tk, time
from tkinter import ttk
from threading import Thread, main_thread

class socket_client:
    def __init__(self, tp, buffer_size = 20, id = "N/A"):
        self.conn = tp[0]
        self.address = tp[1]
        self.data_archive = []
        self.oldlen = 0
        self.newlen = 0
        self.buffer_size = buffer_size
        if id == "N/A": self.name = tp[1][0]
        else: self.name = id

class socket_window():
    def __init__(self, root, parameters):
        self.Text = tk.Text(root, height=20)
        self.grid(column = 0, row= self, sticky = tk.S, padx = 5, pady = 5)


def server_connect(server, host = ("", 65432), timeout = 1):
    server.settimeout(timeout)
    server.bind(host)
    server.listen()

def client_connect(server, client_list):
    while shutdown == False and main_thread().is_alive():
        try:
            client_list.append(socket_client(server.accept(), id = "ID {}".format(len(client_list) + 1)))
            print("client2")
            name = send_data(client_list[-1].conn, "NAME?")
            print("client3")
            client_list[-1].name = name
            print(f"Client IP {client_list[-1].address[0]}, Port {client_list[-1].address[1]}, connect with name {client_list[-1].name}")
        except TimeoutError:
            pass
        time.sleep(0.5)

def send_data(conn, data):
    conn.sendall(str.encode(data))
    try:
        received = conn.recv(4096)
        if received != b"":
            received = str(received)[2:-1]
            return(received)
    except:
        return("N/A")

def receive_data(client):
    try:
        data = client.conn.recv(4096)
        if data != b"":
            data = str(data)[2:-1]
            client.data_archive.append(str(data))
            client.conn.sendall(str.encode("Received {} from {}".format(data, client.name)))
    except:
        return()

def main():
    global shutdown
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address, server_port = ("127.0.0.1", "65432")
    host_addr = (server_address, int(server_port))
    client_list = []
    shutdown = False
    server_connect(server, host_addr, 0.1)
    client_connect_thread = Thread(target=client_connect, args=(server, client_list)).start()
    while shutdown == False:
        for client in client_list:
            receive_data(client)
            if len(client.data_archive) > 0: 
                if client.data_archive[-1].casefold() == "shutdown": shutdown = True
            if len(client.data_archive) > client.buffer_size: 
                client.data_archive.pop(0)
                client.oldlen += -1
            client.newlen = len(client.data_archive)
            if client.newlen != client.oldlen:
                for i in range(len(client.data_archive)):
                    print(f'Client "{client.name}" BI{i}: {client.data_archive[i]}')
            client.oldlen = client.newlen
        time.sleep(0.1)
    shutdown = True

main()