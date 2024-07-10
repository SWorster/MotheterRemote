"""
Runs on host computer, sends a command and gets responses.
"""

import os
import threading
import socketserver
import socket
import time

# python module imports
import ui_commands
import configs
import parse_response

# values from config file
ethernet = configs.rpi_is_ethernet
wifi = configs.rpi_is_wifi
cellular = configs.rpi_is_cellular

host_addr = configs.host_addr
rpi_addr = configs.rpi_addr
rpi_name = configs.rpi_name

so_encoding = configs.utf8
host_port = configs.host_server
host_client = configs.host_client
rpi_port = configs.rpi_server
rpi_client = configs.rpi_client

host_data_path = configs.host_data_path
rpi_data_path = configs.rpi_data_path
rpi_repo = configs.rpi_repo

if ethernet:
    rpi_addr = configs.rpi_hostname

utf8 = configs.utf8
EOF = configs.EOF
EOL = configs.EOL

# global
t1: threading.Thread | None = None
global_ui: bool = False
trigger_prompt: bool = False


class Server:
    def __init__(self):
        print(f"Creating host server {host_addr}:{host_port}")
        socketserver.TCPServer.allow_reuse_address = True  # allows reconnecting

        # start TCP server
        self.server = socketserver.TCPServer(
            (host_addr, host_port), ThreadedTCPRequestHandler
        )

        # run server in designated thread
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
            sock.connect((rpi_addr, rpi_port))  # connect to server
            sock.sendall(f"{m}".encode())  # send everything
            print(f"Sent: {m}")
        except Exception as e:
            print(e)  # print error without halting
            print("Client RPi might not be running rpi_wifi.py")
            start_listener()  # force RPi to run rpi_wifi.py
            time.sleep(5)  # give time for program to start before continuing
        finally:
            sock.close()  # die


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """overwrites TCPServer with custom handler"""

    pass


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    """overwrites BaseRequestHandler with custom handler"""

    def handle(self):
        """custom request handler for TCP threaded server"""
        # ensure request is socket
        if not isinstance(self.request, socket.socket):
            print("ThreadedTCPRequestHandler: self.request not socket")
            return

        # when request comes in, decode and format it
        self.data = self.request.recv(1024).decode(utf8).strip()
        cur_thread = threading.current_thread()
        print(
            f"Received from {self.client_address[0]} in {cur_thread.name}: {self.data}"
        )
        prettify(self.data)  # print formatted data to terminal


def start_listener():
    """sends command to prompt RPi to start listening"""
    # nohup allows rpi_wifi.py to run even after terminal ends
    # & lets process run the the background
    s = [f"ssh {rpi_name}@{rpi_addr} 'cd {rpi_repo}; nohup python3 rpi_wifi.py' &"]
    print("Sending command to RPi:", s)
    to_kill = threading.Thread(target=os.system, args=s)  # run in dedicated thread
    to_kill.start()


def kill_listener():
    """kills RPi program"""
    s = f"ssh {rpi_name}@{rpi_addr} 'pkill -f rpi_wifi.py'"
    print("Sending command to RPi:", s)
    os.system(s)


def prettify(m: str) -> None:
    """prints formatted response from RPi

    Args:
        m (str): message to format
    """
    arr = m.split(EOL)
    for s in arr:
        print(parse_response.sort_response(s))
    global trigger_prompt
    trigger_prompt = True  # allow next user input


def loop():
    """user input loop"""
    global conn
    while True:
        d = input("Type message to send: ")
        if d == "ui":
            d = ui_commands.command_menu()
        elif d == "rsync" or "" or "sync":
            rsync()
            continue
        elif d == "kill":
            kill_listener()
        elif d == "exit":
            print("ending program")
            exit()
        conn.send_to_rpi(d)  # if message exists, send it
        global trigger_prompt
        start = time.time()
        while (time.time() - start < 1.5) and trigger_prompt == False:
            pass  # do nothing until current prompt dealt with, or timeout
        trigger_prompt = False  # disallow user input


def rsync() -> None:
    s = f"rsync -avz -e ssh {rpi_name}@{rpi_addr}:{rpi_data_path} {host_data_path}"
    os.system(s)


def main() -> None:
    """parses arguments"""
    global conn
    conn = Server()  # start TCP server

    l = threading.Thread(target=loop)
    l.start()


if __name__ == "__main__":
    main()
