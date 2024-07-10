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
        print(f"Creating RPi server {rpi_addr}:{rpi_port}")
        socketserver.TCPServer.allow_reuse_address = True  # allows reconnecting

        # start TCP server
        self.server = socketserver.TCPServer(
            (rpi_addr, rpi_port), ThreadedTCPRequestHandler
        )

        # run server in designated thread
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.daemon = True  # Exit server thread when main thread terminates
        server_thread.start()
        print("Server loop running in", server_thread.name)

    def send_to_host(self, m: str) -> None:
        """simple socket connection that forwards a single message to the host, then dies

        Args:
            m (str): message to send
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect((host_addr, host_port))  # connect to server
            sock.sendall(f"{m}".encode())  # send everything
            print(f"Sent: {m}")  # for debugging
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
        global output
        output.rpi_to_client(self.data)  # forward message to radio/sensor


def loop():
    """loops in a dedicated thread. pulls messages from the child connection's buffer and sends them."""
    global output, conn
    cur_thread = threading.current_thread()
    print("Listener loop running in thread:", cur_thread.name)
    while True:
        time.sleep(1)
        d = output.client_to_rpi()  # get messages from child
        if len(d) > 0:
            conn.send_to_host(EOL.join(d))  # if message exists, send it


def main():
    """when program is run, creates server for Wifi connection from host, creates socket to send to host, sets up connection to lora radio or sensor."""
    global output, conn
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

    conn = Server()  # start TCP server


if __name__ == "__main__":
    main()
