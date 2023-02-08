import socket, tkinter as tk, time, traceback
from tkinter import ttk
from threading import Thread, main_thread

tickrate = 1/60
socket_list = []
socket_window_list = []
server_listen = False
shutdown = False
root = tk.Tk()
notebook = ttk.Notebook(root)
auto_res_list = {"NAME?":socket.gethostname(),
                 "TestAutoReceived":"TestAutoSend"}

class socket_connection():
    def __init__(self, *args, **kwargs):
        if kwargs['mode'].casefold() == "SERVER".casefold():
            self.socket = kwargs['socket']
            self.mode = kwargs['mode'].casefold()
            self.conn = kwargs['conn']
            self.address = kwargs['address']
            self.data_archive = []
            self.oldlen = 0
            self.newlen = 0
            self.buffer_size = kwargs['buffer_size']
            self.name = kwargs['ip']
        elif kwargs['mode'].casefold() == "CLIENT".casefold():
            self.socket = kwargs['socket']
            self.mode = kwargs['mode'].casefold()
            #self.conn = kwargs['conn']
            self.address = kwargs['address']
            self.data_archive = []
            self.oldlen = 0
            self.newlen = 0
            self.buffer_size = kwargs['buffer_size']
            self.name = kwargs['ip']

class socket_connection_window():
    def __init__(self, root, notebook, name, socket):
        self.root = root
        self.frame = ttk.Frame(notebook)
        self.frame.grid(row=0,
                        column=0,
                        columnspan=3,
                        sticky=tk.N)

        self.Text = tk.Text(self.frame,
                            width = 85)

        self.Text.grid(row=1,
                       column=0,
                       columnspan=3,
                       sticky=tk.N)

        self.scrollb = ttk.Scrollbar(self.frame,
                                     command=self.Text.yview)

        self.scrollb.grid(row=1,
                          column=3,
                          sticky='nsew')

        self.Text['yscrollcommand'] = self.scrollb.set
        self.entry_data = ttk.Entry(self.frame,
                                    width=90)

        self.entry_data.grid(row=2,
                             column=0,
                             sticky=tk.N,
                             padx=2,
                             pady=5)

        self.button_send = ttk.Button(self.frame,
                                      text = "Send",
                                      command=lambda x = 0: send_data(socket, self.entry_data.get()))

        self.button_send.grid(row=2,
                              column=1,
                              sticky=tk.N,
                              padx=2,
                              pady=3)

        notebook.add(self.frame,
                     text=name)

class main_window():
    def __init__(self, root, frame, name, mode):
        self.root = root
        self.frame = frame
        self.label_top = ttk.Label(self.frame,
                                   text=name)

        self.label_top.grid(row=0,
                            column=0,
                            columnspan=3,
                            sticky=tk.N)

        self.label_ip = ttk.Label(self.frame,
                                  text="IP Address")

        self.label_ip.grid(row=1,
                           column=0,
                           sticky=tk.NW,
                           padx=5)

        self.label_port = ttk.Label(self.frame,
                                    text="Port")

        self.label_port.grid(row=1,
                             column=1,
                             sticky=tk.NW,
                             padx=5)

        self.Var_IP = tk.StringVar()

        self.entry_IP = ttk.Entry(self.frame,
                                  textvariable=self.Var_IP)

        self.entry_IP.grid(row=2,
                           column=0,
                           sticky=tk.NW,
                           padx=5)

        self.Var_Port = tk.StringVar()

        self.entry_Port = ttk.Entry(self.frame,
                                    textvariable=self.Var_Port)

        self.entry_Port.grid(row=2,
                             column=1,
                             sticky=tk.NW,
                             padx=5)

        if mode == "client":
            self.entry_IP.insert(0, "127.0.0.1")     
            self.entry_Port.insert(0, "65432")
            button_connect = ttk.Button(self.frame,
                                        text="Connect",
                                        command=lambda x = 0: client_to_server_connect(self.entry_IP.get(), self.entry_Port.get()))

            button_connect.grid(row=2,
                                column=2,
                                sticky=tk.N)
        if mode == "server":
            self.entry_Port.insert(0, "65432")
            self.tkbool_listen = tk.BooleanVar()
            self.check_listen = ttk.Checkbutton(self.frame,
                                                text='Listen',
                                                command=lambda x = 0: set_server_listen_thread(self.entry_IP.get(), self.entry_Port.get(), self.tkbool_listen.get()),
                                                variable=self.tkbool_listen,
                                                onvalue=True,
                                                offvalue=False)
            self.check_listen.grid(row=2,
                                   column=2,
                                   sticky=tk.N,
                                   pady=2)

def set_server_listen_thread(ip_address, port, var_bool, *args, **kwargs):
    global server_listen
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setblocking(False)
    #server_socket.settimeout(0.1)
    connection_address = (ip_address, int(port))
    if var_bool:
        server_listen = True
        server_socket.bind(connection_address)
        server_socket.listen()
        Thread(target=server_listen_thread, args=(server_socket,)).start()
    else:
        server_socket.close()
        server_listen = False

def server_listen_thread(server):
    global shutdown, server_listen, socket_list, socket_window_list
    while server_listen and not shutdown and main_thread().is_alive():
        try:
            connection = server.accept()
            s = socket_connection(mode="SERVER", 
                                  socket=connection, 
                                  ID="ID {}".format(len(socket_list)+1), 
                                  conn=connection[0], 
                                  address=connection[1], 
                                  buffer_size=120, 
                                  ip=connection[1][0])
            send_data(s, "NAME?")
            time.sleep(tickrate)
            receive_data(s)
            print(s.data_archive)
            if len(s.data_archive)>0: s.name = s.data_archive[-1][10:]
            print(f"Client IP {s.address[0]}, Port {s.address[1]}, connect with name {s.name}")
            socket_window_list.append(socket_connection_window(root, notebook, s.name, s))
            socket_list.append(s)
        except TimeoutError:
            time.sleep(tickrate)
        except BlockingIOError:
            time.sleep(tickrate)
        except:
            traceback.print_exc()
            time.sleep(tickrate)

def client_to_server_connect(ip_address, port):
    global root, notebook, socket_list, socket_window_list
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(1)
    host = (ip_address, int(port))
    try:
        client_socket.connect(host)
        data_received = client_socket.recv(4096)
        print(data_received)
        if data_received == b"NAME?":
            print("teste")
            client_socket.sendall(str.encode(socket.gethostname()))
            print("teste2")
        s = socket_connection(mode="CLIENT", socket=client_socket, ID="ID {}".format(len(socket_list)+1), address=host, buffer_size=120, ip=host[0])
        socket_list.append(s)
        socket_window_list.append(socket_connection_window(root, notebook, "Host IP:{} - PORT:{}".format(host[0], host[1]), s))
    except TimeoutError:
        pass
        time.sleep(tickrate)
    except BlockingIOError:
        time.sleep(tickrate)
    except Exception:
        traceback.print_exc()
        time.sleep(tickrate)
        pass
    
def data_listen_thread():
    global shutdown, socket_list, socket_window_list, tickrate
    while not shutdown and main_thread().is_alive():
        for socket in socket_list:
            try:
                receive_data(socket)
            except TimeoutError:
                time.sleep(tickrate)
                pass
            except BlockingIOError:
                time.sleep(tickrate)
            except Exception:
                traceback.print_exc()
                time.sleep(tickrate)
                pass
            if len(socket.data_archive) > 0:
                if socket.data_archive[-1].casefold() == "shutdown":
                    shutdown = True
                    socket_window_list[socket_list.index(socket)].frame.destroy()
                elif socket.data_archive[-1].casefold() == "disconnect":
                    socket_window_list[socket_list.index(socket)].frame.destroy()
                    socket_list.remove(socket)
                if len(socket.data_archive) > socket.buffer_size:
                    socket_window_list[socket_list.index(socket)].Text.delete("1.0", "2.0")
                    socket.data_archive.pop(0)
                socket.newlen = len(socket.data_archive)
                while socket.newlen != socket.oldlen:
                    socket_window_list[socket_list.index(socket)].Text.insert(str(socket.newlen) + str(".0"), socket.data_archive[socket.oldlen] + "\n")
                    socket_window_list[socket_list.index(socket)].Text.see("end")
                    socket.oldlen += 1      
        time.sleep(tickrate)

def send_data(socket, data):
    try:
        if socket.mode.casefold() == 'server':
            socket.conn.sendall(str.encode(data))
        elif socket.mode.casefold() == 'client':
            socket.socket.sendall(str.encode(data))
        socket.data_archive.append(str("Sent: {}".format(data)))
    except TimeoutError:
        time.sleep(tickrate)
    except Exception:
        traceback.print_exc()
        pass


def receive_data(socket):
    try:
        if socket.mode.casefold() == 'server':
            data = socket.conn.recv(4096)
        elif socket.mode.casefold() == 'client':
            data = socket.socket.recv(4096)
        if data != b"":
            data = str(data)[2:-1]
            socket.data_archive.append(str("Received: {}".format(data)))
            if data in auto_res_list: send_data(socket, auto_res_list[data])
            print("Received {} from {}".format(data, socket.name))
    except TimeoutError:
        time.sleep(tickrate)
    except BlockingIOError:
        time.sleep(tickrate)
    except Exception:
        traceback.print_exc()
        time.sleep(tickrate)
        pass

def main():
    global root, notebook
    root.title("Zeus")
    root.geometry("700x560")
    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    root.rowconfigure(2, weight=4)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.columnconfigure(2, weight=1)
    
    notebook.grid(row=2, column=0, columnspan=3, sticky=tk.N)

    frame_connect_client = ttk.LabelFrame(root)
    frame_connect_client.grid(row=0, column=0, sticky=tk.N)
    frame_connect_server = ttk.LabelFrame(root)
    frame_connect_server.grid(row=0, column=1, sticky=tk.N)

    main_window(root, frame_connect_client, "Client", "client")
    main_window(root, frame_connect_server, "Server", "server")

    Thread(target=data_listen_thread).start()
    

    root.mainloop()

if __name__ == '__main__':
    main()