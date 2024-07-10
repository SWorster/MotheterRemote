"""
Handles WiFi communication for the RPi. Forwards messages from host to radio/sensor, and from radio/sensor back to host.
"""

import socket
import time
import threading
import socketserver

# module imports
import configs
import sensor
import lora_parent

# config settings
host_addr = configs.host_addr
rpi_addr = configs.rpi_addr

host_port = configs.host_server
host_client = configs.host_client
rpi_port = configs.rpi_server
rpi_client = configs.rpi_client
device_type = configs.device_type

so_msg_size = configs.so_msg_size
utf8 = configs.utf8
TTL = configs.TTL  # minutes to wait before quitting
TRIES = configs.TRIES  # number of attempts to make
timeout = time.time() + 60 * TTL
ethernet = configs.rpi_is_ethernet  # we can adapt this program to work with ethernet
rpi_hostname = configs.rpi_hostname
lora = configs.rpi_is_radio
lora_port = configs.rpi_lora_port
EOL = configs.EOL
EOF = configs.EOF


class Server:
    def __init__(self):
        # Create the server, binding to localhost on specified port
        print(f"creating rpi server {rpi_addr}:{rpi_port}")
        self.server = socketserver.TCPServer(
            (rpi_addr, rpi_port), ThreadedTCPRequestHandler
        )
        server_thread = threading.Thread(target=self.server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        print("Server loop running in thread:", server_thread.name)

    def send_to_host(self, m: str) -> None:
        """simple socket connection that forwards a single message to the host, then dies

        Args:
            m (str): message to send
        """
        print("send_to_host")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect((host_addr, host_port))  # Connect to server and send data
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
        global output
        output.rpi_to_client(self.data)  # forward message to radio/sensor


def loop():
    """loops in a dedicated thread. every second, pulls messages from the child connection's buffer and sends them."""
    global output, conn
    cur_thread = threading.current_thread()
    print("Listener loop running in thread:", cur_thread.name)
    while True:
        time.sleep(1)
        d = output.client_to_rpi()  # get messages from child
        if len(d) > 0:
            print("data:      ", d)
            conn.send_to_host(str(d))  # if message exists, send it


def main():
    """when program is run, creates server for Wifi connection from host, creates socket to send to host, sets up connection to lora radio or sensor."""
    global output, conn
    conn = Server()  # start TCP server
    if lora:
        output = lora_parent.Radio()
    else:
        if device_type == "SQM-LU":
            output = sensor.SQMLU()
        elif device_type == "SQM-LE":
            output = sensor.SQMLE()
        else:
            output = sensor.SQMLU()  # default
        output.start_continuous_read()

    l = threading.Thread(target=loop)
    l.start()


if __name__ == "__main__":
    main()
