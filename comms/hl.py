import socket
import sys
import configs

HOST = configs.rpi_addr
PORT = configs.so_port
data = " ".join(sys.argv[1:])

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    sock.sendall((data + "\n").encode())
    received = sock.recv(1024)  # Receive data from the server and shut down
finally:
    sock.close()

print("Sent:     {}".format(data))
print("Received: {}".format(received))
