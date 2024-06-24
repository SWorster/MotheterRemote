# runs on host computer, generates a command from user interface
import argparse
import os
import time
import ui_commands
import configs
import socket

sensor_name = configs.sensor_name
sensor_addr = configs.sensor_addr

host_data_path = configs.host_data_path
client_data_path = configs.client_data_path
client_repo_path = configs.client_repo_path


def client(command: str):
    s = f"ssh {sensor_name}@{sensor_addr} 'python3 {client_repo_path}/rpi_listener.py'"
    print(s)
    # os.system(s)
    time.sleep(5)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a socket object
    server_ip = configs.sensor_addr  # server's IP address
    server_port = configs.socket_port
    print("socket created")
    client.connect((server_ip, server_port))  # establish connection with server
    print("connected")

    while True:
        client.send(command.encode("utf-8")[:1024])
        response = client.recv(1024)  # receive message from the server
        response = response.decode("utf-8")

        print(f"Received: {response}")

        # if server sent us "closed" in the payload, we break out of the loop and close our socket
        if "closed" in response.lower():
            print("received order to close socket")
            client.close()
            print("Connection to server closed")
            break

    # close client socket (connection to the server)
    client.close()
    print("Connection to server closed")


def send_ssh(command: str) -> None:
    """sends a command from the host to the client RPi

    Args:
        s (str): command to send
    """
    if command == "":
        print("Message empty, not sending")
        return
    s = f"ssh {sensor_name}@{sensor_addr} 'python3 {client_repo_path}/rpi_to_sensor.py {command}'"
    print(s)
    os.system(s)


# if __name__ == "__main__":
def main() -> None:
    """parses arguments"""
    parser = argparse.ArgumentParser(
        prog="get_command.py",
        description="Sends a command to the raspberry pi",
        epilog=f"If no argument given, runs user interface",
    )

    parser.add_argument(
        "command",
        nargs="?",
        type=str,
        help="To send a command you've already made, just give it as an argument",
    )

    parser.add_argument(
        "-get", "-g", action="store_true", help="syncs data from sensor"
    )

    parser.add_argument("-ui", "-u", action="store_true", help="enables user interface")

    args = vars(parser.parse_args())

    get = args.get("get")
    if isinstance(get, bool) and get:
        s = f"rsync -avz -e ssh {sensor_name}@{sensor_addr}:{client_data_path} {host_data_path}"
        print(s)
        os.system(s)

    ui = args.get("ui")
    command = args.get("command")
    if isinstance(ui, bool) and ui:
        command = ui_commands.command_menu()

    if command != None:
        client(command)


main()
