"""
Runs on host computer, sends a command and gets responses.
"""

import argparse
import os
import time
import random
import threading

# python module imports
import ui_commands
import configs
import socket
import parse_response

# values from config file
rpi_name = configs.rpi_name
rpi_addr = configs.rpi_addr

so_msg_size = configs.so_msg_size
so_encoding = configs.utf8
so_port = configs.so_port

host_data_path = configs.host_data_path
rpi_data_path = configs.rpi_data_path
rpi_repo = configs.rpi_repo

# global
t1: threading.Thread | None = None


def generate_port() -> None:
    """generates random serial port"""
    global so_port
    so_port = random.randint(10000, 65353)


def start_listener():
    """sends command to prompt RPi to start listening"""
    s = f"ssh {rpi_name}@{rpi_addr} 'cd {rpi_repo}; python3 -m rpi_listener {so_port}'"
    print(s)
    os.system(s)


def start_socket(command: str) -> None:
    """to be reworked: handles socket communication

    Args:
        command (str): command to send
    """
    time.sleep(1)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a socket object
    print("Socket created...")
    client.connect((rpi_addr, so_port))  # establish connection with server

    while True:
        client.send(command.encode(so_encoding)[:so_msg_size])
        response = client.recv(so_msg_size)  # receive message from the server
        response = response.decode(so_encoding)
        data = response.split("\n")[0]
        print(f"Received: {data}")
        formatted_data = parse_response.sort_response(data)

        # if server sent us "closed" in the payload, we break out of the loop and close our socket
        if "closed" in response.lower():
            client.close()
            break

    # close client socket (connection to the server)
    client.close()
    print("Connection to RPi closed")
    if isinstance(t1, threading.Thread):
        t1.join()
    time.sleep(0.1)
    print(formatted_data)


def run_thing(command: str):
    """starts listeners

    Args:
        command (str): command to send
    """

    t1 = threading.Thread(target=start_listener)
    t2 = threading.Thread(target=start_socket, args=[command])

    t1.start()
    t2.start()


def main() -> None:
    """parses arguments"""
    parser = argparse.ArgumentParser(
        prog="get_command.py",
        description="Sends a command to the raspberry pi",
        epilog=f"If no argument given, syncs collected data",
    )
    parser.add_argument(
        "command",
        nargs="?",
        type=str,
        help="To send a command you've already made, just give it as an argument",
    )
    parser.add_argument("-ui", "-u", action="store_true", help="enables user interface")

    args = vars(parser.parse_args())  # get arguments from command line
    ui = args.get("ui")
    command = args.get("command")

    if isinstance(ui, bool) and ui:  # if user wants interface
        command = ui_commands.command_menu()  # get command from user
    if command != None:  # if there's a command to send, send it
        generate_port()
        run_thing(command)

    else:  # if no arguments/flags, just get data
        s = f"rsync -avz -e ssh {rpi_name}@{rpi_addr}:{rpi_data_path} {host_data_path}"
        print(s)
        os.system(s)


if __name__ == "__main__":
    main()
