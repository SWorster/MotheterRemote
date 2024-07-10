"""
Runs on host computer, sends a command and gets responses.
"""

# import os
import threading
import socketserver
import socket
import time

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
trigger_prompt: bool = False


class Server:
    def __init__(self):
        # Create the server, binding to localhost on specified port
        print(f"Creating host server {host_addr}:{host_port}")
        socketserver.TCPServer.allow_reuse_address = True
        self.server = socketserver.TCPServer(
            (host_addr, host_port), ThreadedTCPRequestHandler
        )
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.daemon = True  # Exit server thread when main thread terminates
        server_thread.start()
        print("Server loop running in", server_thread.name)

    def send_to_rpi(self, m: str) -> None:
        """simple socket connection that forwards a single message to the host, then dies

        Args:
            m (str): message to send
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect((rpi_addr, rpi_port))  # Connect to server and send data
            sock.sendall(f"{m}".encode())  # send everything
        except Exception as e:
            print(e)
            print("Client RPi might not be running rpi_wifi.py")
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
            f"Received from {self.client_address[0]} in {cur_thread.name}: {self.data}"
        )  # for debugging
        prettify(self.data)


def prettify(m: str) -> None:
    arr = m.split(EOL)
    for s in arr:
        print(parse_response.sort_response(s))
    global trigger_prompt
    trigger_prompt = True


def loop():
    global conn
    while True:
        d = input("Type message to send: ")
        conn.send_to_rpi(d)  # if message exists, send it
        global trigger_prompt
        start = time.time()
        while (time.time() - start < 1.5) and trigger_prompt == False:
            pass
        trigger_prompt = False


def main() -> None:
    """parses arguments"""
    global conn
    conn = Server()  # start TCP server

    l = threading.Thread(target=loop)
    l.start()


if __name__ == "__main__":
    main()
