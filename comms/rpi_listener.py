import socket
import configs
import rpi_to_sensor
import time
import os

# config settings
server_ip = configs.rpi_addr
port = configs.so_port
socket_msg_size = configs.so_msg_size
socket_encoding = configs.so_encoding
TTL = configs.TTL  # minutes to wait before quitting
TRIES = configs.TRIES  # number of attempts to make


def echo(s: str):
    """fancy print statement"""
    os.system(f"echo '{s}'")


echo("Activating listener...")
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((server_ip, port))  # bind the socket to a specific address and port
server.listen(5)  # listen for incoming connections
echo(f"Listening on {server_ip}:{port}")

client, client_address = server.accept()  # accept incoming connections
echo(f"Accepted connection from {client_address[0]}:{client_address[1]}")

# break while after X attempts or X minutes
timeout = time.time() + 60 * TTL
test = TRIES

while True:
    if test == 0 or time.time() > timeout:
        break
    test = test - 1

    request_bytes = client.recv(socket_msg_size)
    request = request_bytes.decode(socket_encoding)

    if request.lower() == "close":
        client.send("closed".encode(socket_encoding))
        break

    echo(f"Received: {request}")
    msg = rpi_to_sensor.to_sensor(request)
    if msg != "":
        echo(f"Sending response {msg}")
        response = msg.encode(socket_encoding)  # convert string to bytes
        client.send(response)
        client.send("closed".encode(socket_encoding))
        break

client.close()
server.close()
echo("Connection to host closed")
