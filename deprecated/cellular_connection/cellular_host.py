import socket
import socket_testing.parse_response as parse_response

MSGLEN = 2048


class Socket:
    def __init__(self, sock: socket.socket | None = None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host: str, port: str) -> None:
        self.sock.connect((host, port))

    def send(self, msg: bytes) -> None:
        total_sent = 0
        while total_sent < MSGLEN:
            sent = self.sock.send(msg[total_sent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            total_sent = total_sent + sent

    def receive(self) -> bytes:
        chunks: list[bytes] = []
        bytes_recd = 0
        while bytes_recd < MSGLEN:
            chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
            if chunk == b"":
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b"".join(chunks)


# class Connection:
#     def __init__(self, port: int):
#         self.s = socket.socket()
#         print("Socket successfully created")

#         port = 12345  # port on host computer

#         self.s.bind(
#             ("", port)
#         )  # bind receiving port, but leave sender open to any connection
#         print("socket bound to %s" % (port))

#         # put the socket into listening mode
#         self.s.listen(5)  # allow up to five connections in queue
#         print("socket is listening")

#     def new_connection(self) -> socket.socket:
#         # s.accept() waits for a connection, returns socket for the connection and address of client
#         c, addr = self.s.accept()
#         print("Got connection from", addr)
#         self.get_data(c)
#         # if not self.verify_client(c):
#         #     print(f"Closing connection to {addr}")
#         #     c.close()
#         return c

#     def verify_client(self, c: socket.socket) -> bool:
#         print("Verifying identity...", end=" ")
#         count = 5
#         while count > 0:
#             msg = c.recv(2048)
#             if len(msg) > 0:
#                 count -= 1
#                 print(msg.decode())
#                 if msg.decode() == "test":
#                     print("OK")
#                     return True
#         print("ERROR: could not verify identity")
#         return False

#     def get_data(self, c: socket.socket):
#         msg = c.recv(2048)
#         if len(msg) > 0:
#             print(msg.decode())
#         # sensor_response.sort_response(msg.decode())

#     def end_connection(self, c: socket.socket):
#         c.close()  # close connection


# def main():
#     conn = Connection(12345)
#     client = conn.new_connection()
#     while True:
#         conn.get_data(client)


# main()
