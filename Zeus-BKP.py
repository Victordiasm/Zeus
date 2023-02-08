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

class socket_data_window():
    def __init__(self, root, notebook, name, client):
        self.root = root
        self.frame = ttk.Frame(notebook)
        self.frame.grid(row=0, column=0, columnspan=3, sticky=tk.N)
        self.Text = tk.Text(self.frame, width = 85)
        self.Text.grid(row=1, column=0, columnspan=3, sticky=tk.N)
        self.scrollb = ttk.Scrollbar(self.frame, command=self.Text.yview)
        self.scrollb.grid(row=1, column=3, sticky='nsew')
        self.Text['yscrollcommand'] = self.scrollb.set
        self.entry_data = ttk.Entry(self.frame, width=90)
        self.entry_data.grid(row=2, column=0, sticky=tk.N, padx=2, pady=5)
        self.button_send = ttk.Button(self.frame, text = "Send", command=lambda x = 0: send_data(client, self.entry_data.get()))
        self.button_send.grid(row=2, column=1, sticky=tk.N, padx=2, pady=3)
        notebook.add(self.frame, text=name)

class socket_connect_window():
    def __init__(self, root, notebook, frame, name, mode):
        self.root = root
        self.frame = frame
        self.label_top = ttk.Label(self.frame, text=name)
        self.label_top.grid(row=0, column=0, columnspan=3, sticky=tk.N)
        self.label_ip = ttk.Label(self.frame, text="IP Address")
        self.label_ip.grid(row=1, column=0, sticky=tk.NW, padx=5)
        self.label_port = ttk.Label(self.frame, text="Port")
        self.label_port.grid(row=1, column=1, sticky=tk.NW, padx=5)
        self.Var_IP = tk.StringVar()
        self.entry_IP = ttk.Entry(self.frame, textvariable=self.Var_IP)
        self.entry_IP.insert(0, "127.0.0.1")
        self.entry_IP.grid(row=2, column=0, sticky=tk.NW, padx=5)
        self.Var_Port = tk.StringVar()
        self.entry_Port = ttk.Entry(self.frame, textvariable=self.Var_Port)
        self.entry_Port.insert(0, "65432")
        self.entry_Port.grid(row=2, column=1, sticky=tk.NW, padx=5)
        if mode == "client":
            button_connect = ttk.Button(self.frame, text="Connect", command=lambda x = 0: client_connect(self.entry_IP.get(), self.entry_Port.get()))
            button_connect.grid(row=2, column=2, sticky=tk.N)
        if mode == "server":
            self.tkbool_listen = tk.BooleanVar()
            self.check_listen = ttk.Checkbutton(self.frame,
                        text='Listen',
                        command=lambda x = 0: set_listen_thread(self.entry_IP.get(), self.entry_Port.get(), self.tkbool_listen.get()),
                        variable=self.tkbool_listen,
                        onvalue=True,
                        offvalue=False)
            self.check_listen.grid(row=2, column=2, sticky=tk.N, pady=2)

def server_bind(server, host = ("", 65432), timeout = 1):
    server.settimeout(timeout)
    server.bind(host)
    server.listen()

def set_listen_thread(ip_address, port, var_bool):
    global client_list, shutdown
    host_addr = (ip_address, int(port))
    if var_bool:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_bind(server, host_addr, 0.1)
        listen_thread = Thread(target=server_listen_thread, args=(server, client_list)).start()
        receive_thread = Thread(target=client_receive_thread, args=()).start()
    else:
        shutdown = True

def server_listen_thread(server, client_list):
    global shutdown, root, notebook
    while shutdown == False and main_thread().is_alive():
        try:
            client_list.append(socket_client(server.accept(), id = "ID {}".format(len(client_list) + 1)))
            send_data(client_list[-1], "NAME?")
            receive_data(client_list[-1])
            if len(client_list[-1].data_archive) > 0: name = client_list[-1].data_archive[-1]
            else: name = "N/A"
            client_list[-1].name = name

            print(f"Client IP {client_list[-1].address[0]}, Port {client_list[-1].address[1]}, connect with name {client_list[-1].name}")
            create_data_window(root, notebook, name, client_list[-1])
        except TimeoutError:
            pass
        time.sleep(0.5)

def client_receive_thread():
    global shutdown, client_list, client_list_window, notebook
    while shutdown == False and main_thread().is_alive():
        for client in client_list:
            receive_data(client)
            if len(client.data_archive) > 0: 
                if client.data_archive[-1].casefold() == "shutdown":
                    shutdown = True
                    client_list_window[client_list.index(client)].frame.destroy()
                elif client.data_archive[-1].casefold() == "disconnect": client_list_window[client_list.index(client)].frame.destroy()
            if len(client.data_archive) > client.buffer_size:
                client_list_window[client_list.index(client)].Text.delete("1.0", "2.0")
                client.data_archive.pop(0)
                client.oldlen += -1
            client.newlen = len(client.data_archive)
            if client.newlen != client.oldlen:
                client_list_window[client_list.index(client)].Text.insert(str(client.newlen) + str(".0"), 'Receive from Client "{}": {}'.format(client.name, client.data_archive[client.newlen - 1]) + "\n")
                client_list_window[client_list.index(client)].Text.see("end")
            client.oldlen = client.newlen
        time.sleep(0.1)
    shutdown = True

def client_connect_thread():
    Teste = 1

# def connect_server(server, host = socket_host("127.0.0.1", "65432"), timeout = 1):
#     server.settimeout(timeout)
#     try:
#         server.connect((host.address, host.port))
#         received = server.recv(4096)
#         if received == b"NAME?":
#             server.sendall(str.encode("Local PC"))
#     except TimeoutError:
#         print("Timeout")    

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

def create_data_window(root, notebook, name, client):
    global client_list_window
    client_list_window.append(socket_data_window(root, notebook, name, client))

def GUI():
    global root, notebook
    root = tk.Tk()
    root.title("Zeus")
    root.geometry("700x560")
    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    root.rowconfigure(2, weight=4)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.columnconfigure(2, weight=1)

    notebook = ttk.Notebook(root)
    notebook.grid(row=2, column=0, columnspan=3, sticky=tk.N)

    frame_connect_client = ttk.LabelFrame(root)
    frame_connect_client.grid(row=0, column=0, sticky=tk.N)
    frame_connect_server = ttk.LabelFrame(root)
    frame_connect_server.grid(row=0, column=1, sticky=tk.N)

    socket_connect_window(root, notebook, frame_connect_client, "Client", "client")
    socket_connect_window(root, notebook, frame_connect_server, "Server", "server")

    root.mainloop()

def main():
    global client_list, client_list_window, shutdown
    shutdown = False
    client_list = []
    client_list_window = []
    GUI()
    

main()