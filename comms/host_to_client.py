"""
Runs on host computer, sends a command and gets responses.
"""

# import os
# import time
import threading
import socketserver
import socket

# python module imports
# import ui_commands
import configs

# import parse_response

# values from config file
ethernet = configs.rpi_is_ethernet
wifi = configs.rpi_is_wifi
cellular = configs.rpi_is_cellular

host_addr = configs.host_addr
rpi_addr = configs.rpi_addr
rpi_name = configs.rpi_name

so_msg_size = configs.so_msg_size
so_encoding = configs.utf8
host_port = configs.host_server
host_client = configs.host_client
rpi_port = configs.rpi_server
rpi_client = configs.rpi_client

host_data_path = configs.host_data_path
rpi_data_path = configs.rpi_data_path
rpi_repo = configs.rpi_repo

rpi_hostname = configs.rpi_hostname + ".local"

utf8 = configs.utf8
EOF = configs.EOF

# global
t1: threading.Thread | None = None
global_ui: bool = False


class Server:
    def __init__(self):
        # Create the server, binding to localhost on specified port
        self.server = socketserver.TCPServer((host_addr, host_port), MyTCPHandler)
        self.server.serve_forever()  # run server forever (until program interrupted)

    def send_to_rpi(self, m: str) -> None:
        """simple socket connection that forwards a single message to the host, then dies

        Args:
            m (str): message to send
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect((rpi_addr, rpi_port))  # Connect to server and send data
            sock.sendall(f"{m}{EOF}".encode())  # send everything
        finally:
            sock.close()  # die
        print(f"Sent: {m}")  # for debugging


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print(f"{self.client_address[0]} wrote: {self.data}")  # print result to console


# class Connection:
#     def __init__(self):
#         if ethernet:
#             self = Wifi()  # same implementation
#         elif wifi:
#             self = Wifi()
#         elif cellular:
#             self = Cellular()
#         else:
#             self = Wifi()

#     def setup(self) -> None:
#         self.ui = False
#         self.direct = False
#         self.listening = True
#         self.taking_input = True
#         self.data: list[str] = []
#         self.t_in = threading.Thread(self.responses())
#         self.t_out = threading.Thread(self.loop())

#     def start_listening_in(self):
#         self.t_in.start()

#     def start_listening_out(self):
#         self.t_out.start()

#     def responses(self) -> None:
#         while self.listening:
#             time.sleep(1)
#             arr = self.return_collected()
#             for m in arr:
#                 print(parse_response.sort_response(m))

#     def loop(self) -> None:
#         def get_ui() -> str | None:
#             u = ui_commands.command_menu()
#             if u == "exit":
#                 self.ui = False
#                 print("exiting user interface command generator")
#                 return
#             if u == "":
#                 return
#             return u

#         def direct_entry() -> str | None:
#             print("Type cancel to stop sending direct commands,")
#             c = input("or enter command to send: ")
#             if c == "cancel":
#                 print("exiting direct entry")
#                 self.direct = False
#                 return
#             return c

#         def no_ui() -> str | None:
#             modes = [
#                 "MODES:",
#                 "direct: enter commands directly",
#                 "ui: user interface command generator",
#                 "sync: retrieve data",
#                 "quit: exit program",
#             ]
#             print("\n".join(modes))
#             command = input("Type mode: ")
#             match command:
#                 case "direct":
#                     print("activating direct command entry")
#                     self.direct = True
#                 case "sync":
#                     self.rsync()
#                 case "ui":
#                     print("activating user interface command generator")
#                     self.ui = True
#                     return
#                 case "quit":
#                     print("exiting loop")
#                     self.taking_input = False
#                     return
#                 case _:
#                     print("input not recognized")
#                     return

#         while self.taking_input:
#             if self.ui:
#                 s = get_ui()
#             elif self.direct:
#                 s = direct_entry()
#             else:
#                 s = no_ui()

#             if s != None:
#                 self.send(s)

#     def return_collected(self) -> list[str]: ...
#     def rsync(self) -> None: ...
#     def send(self, m: str) -> None: ...
#     def close(self) -> None: ...


# class Wifi(Connection):
#     def __init__(self):
#         self.start_connection()
#         self.setup()

#     def start_connection(self) -> None:
#         self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         # bind the socket to a specific address and port
#         # self.s.bind((host_addr, so_port))
#         self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         print(f"Connecting to {rpi_addr}:{rpi_port}")
#         self.s.connect((rpi_addr, rpi_port))
#         # self.s.listen(5)
#         # print(f"Listening on {rpi_addr}:{so_port}")
#         # c, c_address = self.s.accept()  # accept incoming connections
#         # self.c = c
#         # print(f"Accepted connection from {c_address[0]}:{c_address[1]}")
#         print(f"Connected to {rpi_addr}:{rpi_port}")
#         self.c = self.s
#         self.t1 = threading.Thread(self.listen())

#     def listen(self) -> None:
#         self.live = True
#         while self.live:
#             m = self.recv()
#             self.data.append(m)

#     def return_collected(self) -> list[str]:
#         d = self.data
#         self.data.clear()
#         return d

#     def send(self, m: str) -> None:
#         msg = m.encode(utf8)
#         self.c.send(msg)

#     def recv(self) -> str:
#         msg_bytes = self.c.recv(so_msg_size)
#         msg = msg_bytes.decode(utf8)
#         return msg

#     def close(self) -> None:
#         print("closing connection")
#         self.s.close()
#         self.c.close()

#     def rsync(self) -> None:
#         s = f"rsync -avz -e ssh {rpi_name}@{rpi_addr}:{rpi_data_path} {host_data_path}"
#         print(s)
#         os.system(s)


# class Ethernet(Connection):
#     def __init__(self):
#         self.start_connection()
#         self.setup()

#     def start_connection(self) -> None:
#         self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         # bind the socket to a specific address and port
#         self.s.bind((host_addr, host_port))
#         self.s.listen(5)
#         print(f"Listening on {rpi_hostname}:{rpi_port}")
#         c, c_address = self.s.accept()  # accept incoming connections
#         self.c = c
#         print(f"Accepted connection from {c_address[0]}:{c_address[1]}")
#         self.t1 = threading.Thread(self.listen())

#     def listen(self) -> None:
#         self.live = True
#         while self.live:
#             m = self.recv()
#             self.data.append(m)

#     def return_collected(self) -> list[str]:
#         d = self.data
#         self.data.clear()
#         return d

#     def send(self, m: str) -> None:
#         msg = m.encode(utf8)
#         self.c.send(msg)

#     def recv(self) -> str:
#         msg_bytes = self.c.recv(so_msg_size)
#         msg = msg_bytes.decode(utf8)
#         return msg

#     def close(self) -> None:
#         print("closing connection")
#         self.s.close()
#         self.c.close()

#     def rsync(self) -> None:
#         s = f"rsync -avz -e ssh {rpi_name}@{rpi_hostname}:{rpi_data_path} {host_data_path}"
#         print(s)
#         os.system(s)


# class Cellular(Connection):
#     pass


def loop():
    global conn
    while True:
        d = input("Type message to send: ")
        conn.send_to_rpi(d)  # if message exists, send it


def main() -> None:
    """parses arguments"""
    global conn
    conn = Server()  # start TCP server

    l = threading.Thread(target=loop)
    l.start()

    # conn = Connection()
    # conn.start_listening_in()
    # conn.start_listening_out()
    # conn.loop()


if __name__ == "__main__":
    main()
