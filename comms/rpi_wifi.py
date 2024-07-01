"""
Handles WiFi communication for the RPi.
"""

import socket
import configs

# import sensor
import time
import threading

# config settings
rpi_addr = configs.rpi_addr
so_port = configs.so_port
so_msg_size = configs.so_msg_size
utf8 = configs.utf8
TTL = configs.TTL  # minutes to wait before quitting
TRIES = configs.TRIES  # number of attempts to make
timeout = time.time() + 60 * TTL


class sock:
    def __init__(self):
        self.data: list[str]
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind the socket to a specific address and port
        self.s.bind((rpi_addr, so_port))
        self.s.listen(5)
        print(f"Listening on {rpi_addr}:{so_port}")
        c, c_address = self.s.accept()  # accept incoming connections
        self.c = c
        print(f"Accepted connection from {c_address[0]}:{c_address[1]}")
        self.t1 = threading.Thread(self.listen())

    def return_collected(self) -> list[str]:
        d = self.data
        self.data.clear()
        return d

    def send(self, m: str):
        msg = m.encode(utf8)
        self.c.send(msg)

    def listen(self):
        self.live = True
        while self.live:
            m = self.recv()
            self.data.append(m)

    def recv(self) -> str:
        msg_bytes = self.c.recv(so_msg_size)
        msg = msg_bytes.decode(utf8)
        return msg

    def close(self):
        self.s.close()
        self.c.close()


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
