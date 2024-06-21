# runs on host computer, generates a command from user interface
import argparse
import os
import ui_commands
import configs

sensor_name = configs.sensor_name

if configs.ddns_over_ip:
    sensor_addr = configs.sensor_ddns
else:
    sensor_addr = configs.sensor_ip

host_data_path = configs.host_data_path
client_data_path = configs.client_data_path
client_repo_path = configs.client_repo_path


def send(s: str):
    os.system(
        f"ssh {sensor_name}@{sensor_addr} 'python3 {client_repo_path}/rpi_to_sensor.py {s}'"
    )


# if __name__ == "__main__":
def main():
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
    if get:
        s = f"rsync -avz -e ssh {sensor_name}@{sensor_addr}:{client_data_path} {host_data_path}"
        os.system(s)

    ui = args.get("ui")
    if ui:
        command = ui_commands.command_menu()
        send(command)
        return

    command = args.get("command")
    if command != None:
        send(command)
        return


main()
