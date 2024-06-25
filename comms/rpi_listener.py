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
utf8 = configs.utf8
TTL = configs.TTL  # minutes to wait before quitting
TRIES = configs.TRIES  # number of attempts to make


def listen() -> None:
    echo("LISTENER:")
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
        request = request_bytes.decode(utf8)

        if request.lower() == "close":
            c.send("closed".encode(utf8))
            break

        echo(f"Received: {request}")
        msg = rpi_to_sensor.to_sensor(request)
        if msg != "":
            response = msg.encode(utf8)  # convert string to bytes
            echo(f"Sending {msg.split("\n")[0]}")
            c.send(response)
            c.send("closed".encode(utf8))
            break
    c.close()
    s.close()
    echo("Connection to host closed")


def echo(s: str):
    """fancy print statement"""
    os.system(f"echo '{s.rjust(100)}'")


def main() -> None:
    """parses arguments"""
    global so_port
    parser = argparse.ArgumentParser(
        prog="rpi_listener.py",
        description="Handles RPi comms with host computer, using socket",
        epilog=f"Can give port number as argument, or defaults to number in configs.py",
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
        so_port = port
    listen()


if __name__ == "__main__":
    main()
