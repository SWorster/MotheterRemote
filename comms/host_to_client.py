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
import parse_response

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
EOL = configs.EOL

# global
t1: threading.Thread | None = None
global_ui: bool = False


class Server:
    def __init__(self):
        # Create the server, binding to localhost on specified port
        print(f"Creating host server {host_addr}:{host_port}")
        self.server = socketserver.TCPServer(
            (host_addr, host_port), ThreadedTCPRequestHandler
        )
        server_thread = threading.Thread(target=self.server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        print("Server loop running in", server_thread.name)

        # self.server = socketserver.TCPServer((host_addr, host_port), MyTCPHandler)
        # self.server.serve_forever()  # run server forever (until program interrupted)

    def send_to_rpi(self, m: str) -> None:
        """simple socket connection that forwards a single message to the host, then dies

        Args:
            m (str): message to send
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect((rpi_addr, rpi_port))  # Connect to server and send data
            sock.sendall(f"{m}".encode())  # send everything
        finally:
            sock.close()  # die
        print(f"Sent: {m}")  # for debugging


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        if not isinstance(self.request, socket.socket):
            print("ThreadedTCPRequestHandler: self.request not socket")
            return
        self.data = self.request.recv(1024).decode(utf8).strip()
        cur_thread = threading.current_thread()
        print(
            f"{self.client_address[0]} {cur_thread.name}: {self.data}"
        )  # for debugging
        prettify(self.data)


def prettify(m: str) -> None:
    arr = m.split(EOL)
    for s in arr:
        print(parse_response.sort_response(s))


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


if __name__ == "__main__":
    main()
