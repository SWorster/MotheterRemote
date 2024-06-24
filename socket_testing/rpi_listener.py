import socket
import configs
import rpi_to_sensor
import time
import os

TTL = 5  # minutes to wait before quitting
TRIES = 5  # number of attempts to make


def echo(s: str):
    os.system(f"echo '{s}'")


echo("Activating listener...")
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_ip = configs.sensor_addr
port = configs.socket_port
socket_msg_size = configs.socket_msg_size
socket_encoding = configs.socket_encoding

server.bind((server_ip, port))  # bind the socket to a specific address and port
server.listen(5)  # listen for incoming connections
echo(f"Listening on {server_ip}:{port}")

client, client_address = server.accept()  # accept incoming connections
echo(f"Accepted connection from {client_address[0]}:{client_address[1]}")

timeout = time.time() + 60 * TTL
test = TRIES

while True:
    if test == 0 or time.time() > timeout:
        break
    test = test - 1

    request_bytes = client.recv(socket_msg_size)
    request = request_bytes.decode(socket_encoding)  # convert bytes to string

    if request.lower() == "close":
        client.send("closed".encode(socket_encoding))
        break

    echo(f"Received: {request}")
    msg = rpi_to_sensor.to_sensor(request)
    if msg != "":
        echo(f"sending response {msg}")
        response = msg.encode(socket_encoding)  # convert string to bytes
        client.send(response)
        client.send("closed".encode(socket_encoding))
        break

client.close()
server.close()
echo("Connection to host closed")
