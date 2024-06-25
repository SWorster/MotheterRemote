# runs on host computer, generates a command from user interface
import argparse
import os
import time
import ui_commands
import configs
import socket
import parse_response

rpi_name = configs.rpi_name
rpi_addr = configs.rpi_addr

so_msg_size = configs.so_msg_size
so_encoding = configs.so_encoding

host_data_path = configs.host_data_path
rpi_data_path = configs.rpi_data_path
rpi_repo_path = configs.rpi_repo_path


def server(command: str) -> None:
    s = f"ssh {rpi_name}@{rpi_addr} 'python3 -m {rpi_repo_path}/rpi_listener.py {configs.so_port}'"
    print(s)
    os.system(s)
    time.sleep(5)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a socket object
    server_ip = configs.rpi_addr  # server's IP address
    server_port = configs.so_port
    print("Socket created...")
    client.connect((server_ip, server_port))  # establish connection with server

    while True:
        client.send(command.encode(so_encoding)[:so_msg_size])
        response = client.recv(so_msg_size)  # receive message from the server
        response = response.decode(so_encoding)
        print(f"Received: {response}")
        data = response.split("\n")[0]
        print(parse_response.sort_response(data))

        # if server sent us "closed" in the payload, we break out of the loop and close our socket
        if "closed" in response.lower():
            client.close()
            break

    # close client socket (connection to the server)
    client.close()
    print("Connection to RPi closed")


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
        server(command)
    else:  # if no arguments/flags, just get data
        s = f"rsync -avz -e ssh {rpi_name}@{rpi_addr}:{rpi_data_path} {host_data_path}"
        print(s)
        os.system(s)


if __name__ == "__main__":
    main()
