import socket
import configs
import rpi_to_sensor
import time
import os
import argparse


# config settings
rpi_addr = configs.rpi_addr
so_port = configs.so_port
so_msg_size = configs.so_msg_size
so_encoding = configs.so_encoding
TTL = configs.TTL  # minutes to wait before quitting
TRIES = configs.TRIES  # number of attempts to make


def listen() -> None:
    echo("Activating listener...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((rpi_addr, so_port))  # bind the socket to a specific address and port
    s.listen(5)  # listen for incoming connections
    echo(f"Listening on {rpi_addr}:{so_port}")

    c, c_address = s.accept()  # accept incoming connections
    echo(f"Accepted connection from {c_address[0]}:{c_address[1]}")

    # break while after X attempts or X minutes
    timeout = time.time() + 60 * TTL
    test = TRIES

    while True:
        if test == 0 or time.time() > timeout:
            break
        test = test - 1

        request_bytes = c.recv(so_msg_size)
        request = request_bytes.decode(so_encoding)

        if request.lower() == "close":
            c.send("closed".encode(so_encoding))
            break

        echo(f"Received: {request}")
        msg = rpi_to_sensor.to_sensor(request)
        if msg != "":
            echo(f"Sending response {msg}")
            response = msg.encode(so_encoding)  # convert string to bytes
            c.send(response)
            c.send("closed".encode(so_encoding))
            break
    c.close()
    s.close()
    echo("Connection to host closed")


def echo(s: str):
    """fancy print statement"""
    os.system(f"echo '{s}'")


def main() -> None:
    """parses arguments"""
    parser = argparse.ArgumentParser(
        prog="rpi_listener.py",
        description="Handles RPi comms with host computer, using socket",
        epilog=f"Can give port number as argument, or defaults to ",
    )
    parser.add_argument(
        "port",
        nargs="?",
        type=int,
        help="Provide a port number, or leave empty to use port number from configs.py",
    )

    args = vars(parser.parse_args())  # get arguments from command line
    port = args.get("port")
    if isinstance(port, int):
        global so_port
        so_port = port
    echo(f"using port {so_port}")


if __name__ == "__main__":
    main()
