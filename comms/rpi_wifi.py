"""
Handles WiFi communication for the RPi. Forwards messages from host to radio/sensor, and from radio/sensor back to host.
"""

import os
import socket
import time
import threading
import socketserver

# module imports
import configs
import sensor
import lora_parent

# WiFi/Ethernet connection info
host_addr = configs.host_addr
rpi_addr = configs.rpi_addr

# socket port numbers
host_server = configs.host_server
rpi_server = configs.rpi_server

# sensor info
device_type = configs.device_type

# text encoding
utf8 = configs.utf8
EOL = configs.EOL
EOF = configs.EOF
msg_len = configs.msg_len

# timing
long_s = configs.long_s
mid_s = configs.mid_s
short_s = configs.short_s

echo = False  # output to log file

# global
output: lora_parent.Radio | sensor.SQMLE | sensor.SQMLU


class Server:
    def __init__(self):
        p(f"Creating RPi server {rpi_addr}:{rpi_server}")
        socketserver.TCPServer.allow_reuse_address = True  # allows reconnecting

        # start TCP server
        self.server = socketserver.TCPServer(
            (rpi_addr, rpi_server), ThreadedTCPRequestHandler
        )

        # run server in designated thread
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.daemon = True  # Exit server thread when main thread terminates
        server_thread.start()
        p(f"Server loop running in {server_thread.name}")

    def send_to_host(self, s: str) -> None:
        """simple socket connection that forwards a single message to the host, then dies

        Args:
            s (str): message to send
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect((host_addr, host_server))  # connect to server
            sock.sendall(f"{s}".encode(utf8))  # send everything
            p(f"Sent: {s}")  # for debugging
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
            p("ThreadedTCPRequestHandler: self.request not socket")
            return

        # when request comes in, decode and format it
        self.data = self.request.recv(msg_len).decode(utf8).strip()
        cur_thread = threading.current_thread()
        p(f"Received from {self.client_address[0]} in {cur_thread.name}: {self.data}")
        global output
        if "rsync" in self.data:
            p("rsync found")
            if isinstance(output, sensor.SQMLU or sensor.SQMLE):
                p("isinstance")
                return  # don't send rsync message to sensor
        try:
            output.rpi_to_client(self.data)  # forward message to radio/sensor
        except Exception as e:
            p(str(e))
            p("Resetting output device")  # probably lost connection
            _device_search()  # reconnect if possible
            time.sleep(long_s)


def _loop() -> None:
    """loops in a dedicated thread. pulls messages from the child connection's buffer and sends them."""
    global output, conn
    cur_thread = threading.current_thread()
    p(f"Listener loop running in {cur_thread.name}")
    while True:
        time.sleep(mid_s)
        s = output.client_to_rpi()  # get messages from child
        if isinstance(s, list):  # message is list, convert to string
            m = EOL.join(s)
            p(f"Sending to host: {m}")
            conn.send_to_host(EOL.join(m))
            return
        if len(s) > 0:  # message is non-empty string
            p(f"Sending to host: {s}")
            conn.send_to_host(s)


def _device_search() -> None:
    """determines whether a radio or sensor is connected by trying to create each device"""
    global output

    try:
        output = lora_parent.Radio()
        return
    except Exception as e:
        p(str(e))
        p(f"No radio found at port {configs.R_ADDR}")
        p("Trying sensor connection...")

    try:
        if device_type == "SQM-LU":
            output = sensor.SQMLU()
        elif device_type == "SQM-LE":
            output = sensor.SQMLE()
        else:
            output = sensor.SQMLU()  # default
        output.start_continuous_read()
        return
    except Exception as e:
        p(str(e))
        p(f"SQM-LU or SQM-LE sensor not found.")

    p("No radio or sensor found. Please check connection!")


def p(s: str) -> None:
    global echo
    if echo:
        os.system(f"echo {s}")
    else:
        print(s, flush=True)  # print, even if in thread


def main():
    """when program is run, creates server for Wifi connection from host, creates socket to send to host, sets up connection to lora radio or sensor."""

    global output, conn

    _device_search()

    l = threading.Thread(target=_loop)
    l.start()

    conn = Server()  # start TCP server


if __name__ == "__main__":
    main()
