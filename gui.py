import socket, tkinter as tk, time
from tkinter import ttk
from threading import Thread, main_thread

class socket_window():
    def __init__(self, root, notebook, name):
        self.root = root
        self.frame = ttk.Frame(notebook)
        self.frame.grid(row=0, column=0, columnspan=3, sticky=tk.N)
        self.Text = tk.Text(self.frame, width = 85)
        self.Text.grid(row=1, column=0, columnspan=3, sticky=tk.N)
        self.entry_data = ttk.Entry(self.frame, width=90)
        self.entry_data.grid(row=2, column=0, sticky=tk.N, padx=2, pady=5)
        self.button_send = ttk.Button(self.frame, text = "Send")
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
            button_connect = ttk.Button(self.frame, text = "Connect", command=lambda x = 0: socket_window(root, notebook, "Client: {}".format(self.Var_IP.get())))
            button_connect.grid(row=2, column=2, sticky=tk.N)
        elif mode == "server":
            self.tkbool_listen = tk.BooleanVar()
            self.check_listen = ttk.Checkbutton(self.frame,
                        text='Listen',
                        command=lambda x = 0: check_send_senf(tkbool_listen),
                        variable=self.tkbool_listen,
                        onvalue=True,
                        offvalue=False)
            self.check_listen.grid(row=2, column=2, sticky=tk.N, pady=2)

def GUI():
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
    

GUI()