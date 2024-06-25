# runs on host computer, generates a command from user interface
import argparse
import os
import time  # type: ignore
import ui_commands
import configs
import socket
import parse_response
import random

rpi_name = configs.rpi_name
rpi_addr = configs.rpi_addr

so_msg_size = configs.so_msg_size
so_encoding = configs.so_encoding
so_port = configs.so_port

host_data_path = configs.host_data_path
rpi_data_path = configs.rpi_data_path
rpi_repo_path = configs.rpi_repo_path


def party_mode() -> None:
    global so_port
    so_port = random.randint(10000, 65353)


def run_remote():
    print("run_remote")
    s = f"ssh {rpi_name}@{rpi_addr} 'cd {rpi_repo_path}; python3 -m rpi_listener {configs.so_port}'"
    print(s)
    os.system(s)


def server(command: str) -> None:
    print("server")
    time.sleep(2)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a socket object
    server_ip = configs.rpi_addr  # server's IP address
    print("Socket created...")
    client.connect((server_ip, so_port))  # establish connection with server

    while True:
        client.send(command.encode(so_encoding)[:so_msg_size])
        response = client.recv(so_msg_size)  # receive message from the server
        response = response.decode(so_encoding)
        print(f"Received: {response}")
        data = response.split("\n")[0]
        parse_response.sort_response(data)  # print formatted data to console

        # if server sent us "closed" in the payload, we break out of the loop and close our socket
        if "closed" in response.lower():
            client.close()
            break

    # close client socket (connection to the server)
    client.close()
    print("Connection to RPi closed")


def run_thing(command: str):
    import threading

    party_mode()
    t1 = threading.Thread(target=run_remote)
    t2 = threading.Thread(target=server, args=[command])

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
        run_thing(command)
    else:  # if no arguments/flags, just get data
        s = f"rsync -avz -e ssh {rpi_name}@{rpi_addr}:{rpi_data_path} {host_data_path}"
        print(s)
        os.system(s)


if __name__ == "__main__":
    main()
