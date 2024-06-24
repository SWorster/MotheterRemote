import socket
import configs
import rpi_to_sensor
import time
import os

# create a socket object
os.system("echo listening...")
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_ip = configs.sensor_addr
os.system("echo listening...")
port = configs.socket_port

os.system("echo listening...")
server.bind((server_ip, port))  # bind the socket to a specific address and port
os.system("echo listening...")
server.listen(5)  # listen for incoming connections
os.system(f"echo 'Listening on {server_ip}:{port}'")

client_socket, client_address = server.accept()  # accept incoming connections
os.system(f"echo 'Accepted connection from {client_address[0]}:{client_address[1]}'")

timeout = time.time() + 60 * 5  # 5 minutes from now
test = 0

while True:
    if test == 5 or time.time() > timeout:
        break
    test = test - 1

    request_bytes = client_socket.recv(1024)
    request = request_bytes.decode("utf-8")  # convert bytes to string

    if request.lower() == "close":
        client_socket.send("closed".encode("utf-8"))
        break

    os.system(f"echo 'Received: {request}'")

    msg = rpi_to_sensor.to_sensor(request)
    if msg != "":
        response = msg.encode("utf-8")  # convert string to bytes
        client_socket.send(response)
        client_socket.send("closed".encode("utf-8"))
        break

client_socket.close()
os.system("echo 'Connection to client closed'")
server.close()
