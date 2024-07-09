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
        self.server = socketserver.TCPServer((rpi_addr, rpi_port), MyTCPHandler)
        self.server.serve_forever()  # run server forever (until program interrupted)

    def send_to_host(self, m: str) -> None:
        """simple socket connection that forwards a single message to the host, then dies

        Args:
            m (str): message to send
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect((host_addr, rpi_client))  # Connect to server and send data
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
        print(f"{self.client_address[0]} wrote: {self.data}")  # for debugging
        global output
        output.rpi_to_client(self.data)  # forward message to radio/sensor


def loop():
    """loops in a dedicated thread. every second, pulls messages from the child connection's buffer and sends them."""
    global output, conn
    while True:
        time.sleep(1)
        d = output.client_to_rpi()  # get messages from child
        if d != "":
            conn.send_to_host(d)  # if message exists, send it


def main():
    """when program is run, creates server for Wifi connection from host, creates socket to send to host, sets up connection to lora radio or sensor."""
    global output, conn
    conn = Server()  # start TCP server
    if lora:
        output = lora_parent.Radio()
    else:
        output = sensor.SQM()

    l = threading.Thread(target=loop)
    l.start()


if __name__ == "__main__":
    main()


# class Radio:
#     def __init__(self):
#         self.data: list[str]
#         self.s = serial.Serial(ADDR, BAUD, timeout=None)
#         self.l = threading.Thread(self.listen())  # listener in background
#         self.l.start()

#     def start_listen(self) -> None:
#         try:
#             self.l.start()
#         except RuntimeError:
#             print("already running listen()")

#     def listen(self) -> None:
#         self.live = True
#         while self.live:
#             full_msg = self.s.read_until(EOF.encode())
#             msg_arr = full_msg.decode().split(EOL)
#             for msg in msg_arr:
#                 self.data.append(msg)

#     def rpi_to_client(self, msg: str | list[str] = "test") -> None:
#         if isinstance(msg, list):
#             m = EOL.join(msg)
#         else:
#             m = msg
#         self.s.write((m + EOF).encode())

#     def return_collected(self) -> list[str]:
#         d = self.data
#         self.data.clear()
#         return d

#     def send_loop(self) -> None:  # ui for debugging only
#         while True:
#             i = input("Send: ")
#             self.rpi_to_client(i)


# def main():
#     # wifi = Wifi()
#     global s
#     if lora:
#         s = Radio()
#         s.l.start()
#     else:
#         s = Sensor()


# if __name__ == "__main__":
#     main()


# class conn:
#     def __init__(self):
#         pass


# class sock:
#     def __init__(self):
#         self.data: list[str]
#         self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         # bind the socket to a specific address and port
#         self.s.bind((rpi_addr, so_port))
#         self.s.listen(5)
#         print(f"Listening on {rpi_addr}:{so_port}")
#         c, c_address = self.s.accept()  # accept incoming connections
#         self.c = c
#         print(f"Accepted connection from {c_address[0]}:{c_address[1]}")
#         self.t1 = threading.Thread(self.listen())

#     def return_collected(self) -> list[str]:
#         d = self.data
#         self.data.clear()
#         return d

#     def send(self, m: str):
#         msg = m.encode(utf8)
#         self.c.send(msg)

#     def listen(self):
#         self.live = True
#         while self.live:
#             m = self.recv()
#             self.data.append(m)

#     def recv(self) -> str:
#         msg_bytes = self.c.recv(so_msg_size)
#         msg = msg_bytes.decode(utf8)
#         return msg

#     def close(self):
#         self.s.close()
#         self.c.close()


# def main():
#     so = sock()
#     so.send("test")
#     lst = so.return_collected()
#     print(lst)


# if __name__ == "__main__":
#     main()

# def listen() -> None:
#     print("LISTENER:")
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.bind((rpi_addr, so_port))  # bind the socket to a specific address and port
#     s.listen(5)  # listen for incoming connections
#     print(f"Listening on {rpi_addr}:{so_port}")

#     c, c_address = s.accept()  # accept incoming connections
#     print(f"Accepted connection from {c_address[0]}:{c_address[1]}")

#     # break while after X attempts or X minutes
#     timeout = time.time() + 60 * TTL
#     test = TRIES

#     while True:
#         if test == 0 or time.time() > timeout:
#             break
#         test = test - 1

#         request_bytes = c.recv(so_msg_size)
#         request = request_bytes.decode(utf8)

#         if request.lower() == "close":
#             c.send("closed".encode(utf8))
#             break

#         print(f"Received: {request}")
#         msg = sensor.send_command(request)
#         if msg != "":
#             response = msg.encode(utf8)  # convert string to bytes
#             data = msg.split("\n")[0]
#             print(f"Sending {data}")
#             c.send(response)
#             c.send("closed".encode(utf8))
#             break
#     c.close()
#     s.close()
#     print("Connection to host closed")
#     exit()
