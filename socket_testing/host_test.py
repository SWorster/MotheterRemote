import socket
import sys

sys.path.append("/sensor_interface")
from socket_testing.get_command import from_socket

s = socket.socket()
print("Socket successfully created")

port = 12345

s.bind(("", port))
print("socket bound to %s" % (port))

# put the socket into listening mode
s.listen(5)
print("socket is listening")

while True:
    c, addr = s.accept()
    print("Got connection from", addr)
    c.send("Thank you for connecting".encode())
    msg = c.recv(1024)
    from_socket(msg.decode())
    # print(msg.decode())
    c.close()
