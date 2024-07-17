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

# WiFi/Ethernet connection info
host_addr = configs.host_addr
rpi_addr = configs.rpi_addr
rpi_name = configs.rpi_name

# socket port numbers
host_server = configs.host_server
rpi_server = configs.rpi_server

# data storage and repository directories
host_data_path = configs.host_data_path
rpi_data_path = configs.rpi_data_path
rpi_repo = configs.rpi_repo

# text encoding
utf8 = configs.utf8
EOF = configs.EOF  # end of file character
EOL = configs.EOL  # end of line character
msg_len = configs.msg_len  # length of message to send/receive

# timing
long_s = configs.long_s
mid_s = configs.mid_s
short_s = configs.short_s

remote_start = configs.remote_start

# global
allow_ui: bool = False  # whether ready to ask for user input
output: object


class Server:
    def __init__(self):
        print(f"Creating host server {host_addr}:{host_server}")
        socketserver.TCPServer.allow_reuse_address = True  # allows reconnecting
        # start TCP server
        try:
            self.server = socketserver.TCPServer(
                (host_addr, host_server), ThreadedTCPRequestHandler
            )
        except Exception as e:
            print(e)
            self.server.server_close()

        # run server in designated thread
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.daemon = True  # Exit server thread when main thread terminates
        server_thread.start()
        print("Server loop running in", server_thread.name)

    def send_to_rpi(self, s: str) -> None:
        """simple socket connection that forwards a single message to the host, then dies

        Args:
            s (str): message to send
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect((rpi_addr, rpi_server))  # connect to server
            sock.sendall(f"{s}".encode(utf8))  # send everything
            print(f"Sent: {s}")
        except Exception as e:
            print(e)  # print error without halting
            print("Client RPi might not be running rpi_wifi.py")
            if remote_start:
                _start_listener()  # force RPi to run rpi_wifi.py
                time.sleep(long_s)  # give time for program to start before continuing
            else:
                print("Wait approx. 1 minute before trying again.")
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
        self.data = self.request.recv(msg_len).decode(utf8).strip()
        cur_thread = threading.current_thread()
        print(
            f"Received from {self.client_address[0]} in {cur_thread.name}: {self.data}"
        )
        _prettify(self.data)  # print formatted data to terminal


def _start_listener():
    """sends command to prompt RPi to start listening"""
    # nohup allows rpi_wifi.py to run even after terminal ends
    # & lets process run the the background
    s = [f"ssh {rpi_name}@{rpi_addr} 'cd {rpi_repo}; nohup python3 rpi_wifi.py' &"]
    print("Sending command to RPi:", s)
    to_kill = threading.Thread(target=os.system, args=s)  # run in dedicated thread
    to_kill.start()


def _kill_listener():
    """kills RPi program"""
    s = f"ssh {rpi_name}@{rpi_addr} 'pkill -f rpi_wifi.py'"
    print("Sending command to RPi:", s)
    os.system(s)


def _prettify(s: str) -> None:
    """prints formatted response from RPi

    Args:
        s (str): message to format
    """
    arr = s.split(EOL)
    for m in arr:
        print(parse_response.sort_response(m))
    global allow_ui
    allow_ui = True  # allow next user input


def _ui_loop():
    """user input loop"""
    global conn, allow_ui
    while True:
        s = input("\nType message to send: ")
        match s:
            case "ui":
                s = ui_commands.command_menu()
            case "rsync" | "sync":
                _rsync()
                continue
            case "kill":
                _kill_listener()
                continue
            case "exit" | "quit" | "q":
                print("Ending program")
                exit()
            case "help":
                s = "Commands:\n\
                    ui: user interface to generate commands\n\
                    rsync | sync: get all recorded data from sensor\n\
                    kill: stop the program running on the RPi\n\
                    exit | quit | q: stop this program\n\
                    help: print this help menu"
                print(s.replace("    ", " "))
                continue
            case _:
                pass

        conn.send_to_rpi(s)  # if message exists, send it
        start = time.time()
        while (time.time() - start < 3) and allow_ui == False:
            pass  # do nothing until current prompt dealt with, or timeout
        allow_ui = False  # disallow user input


def _rsync() -> None:
    """runs rsync command. also sends an rsync trigger in case radio is used"""
    s = f"rsync -avz -e ssh {rpi_name}@{rpi_addr}:{rpi_data_path} {host_data_path}"
    os.system(s)
    conn.send_to_rpi("rsync")


def main() -> None:
    """starts server and listens for incoming communications"""
    global conn, output
    conn = Server()  # start TCP server

    l = threading.Thread(target=_ui_loop)
    l.start()


if __name__ == "__main__":
    main()
