"""
Runs on host computer, sends a command and gets responses.
"""

import argparse
import os
import time
import threading

# python module imports
import ui_commands
import configs
import socket
import parse_response

# values from config file
ethernet = configs.rpi_is_ethernet
wifi = configs.rpi_is_wifi
cellular = configs.rpi_is_cellular

host_addr = configs.host_addr
rpi_addr = configs.rpi_addr
rpi_name = configs.rpi_name

so_msg_size = configs.so_msg_size
so_encoding = configs.utf8
so_port = configs.so_port

host_data_path = configs.host_data_path
rpi_data_path = configs.rpi_data_path
rpi_repo = configs.rpi_repo

rpi_hostname = configs.rpi_hostname

utf8 = configs.utf8

# global
t1: threading.Thread | None = None
global_ui: bool = False


class Connection:
    def __init__(self):
        self.ui = False
        self.direct = False
        if ethernet:
            self = Wifi()  # same implementation
        elif wifi:
            self = Wifi()
        elif cellular:
            self = Cellular()
        else:
            self = Wifi()

        self.listening = True
        self.taking_input = True
        self.t_in = threading.Thread(self.output())
        self.t_out = threading.Thread(self.loop())
        self.t_in.start()
        self.t_out.start()

    def output(self) -> None:
        while self.listening:
            time.sleep(1)
            arr = self.return_collected()
            for m in arr:
                print(parse_response.sort_response(m))

    def get_ui(self) -> str | None:
        u = ui_commands.command_menu()
        if u == "exit":
            self.ui = False
            print("exiting user interface command generator")
            return
        if u == "":
            return
        return u

    def direct_entry(self) -> str | None:
        print("Type cancel to stop sending direct commands,")
        c = input("or enter command to send: ")
        if c == "cancel":
            print("exiting direct entry")
            self.direct = False
            return
        return c

    def no_ui(self) -> str | None:
        modes = [
            "MODES:",
            "direct: enter commands directly",
            "ui: user interface command generator",
            "sync: retrieve data",
            "quit: exit program",
        ]
        print("\n".join(modes))
        command = input("Type mode: ")
        match command:
            case "direct":
                print("activating direct command entry")
                self.direct = True
            case "sync":
                self.rsync()
            case "ui":
                print("activating user interface command generator")
                self.ui = True
                return
            case "quit":
                print("exiting loop")
                self.taking_input = False
                return
            case _:
                print("input not recognized")
                return

    def loop(self) -> None:
        while self.taking_input:
            if self.ui:
                s = self.get_ui()
            elif self.direct:
                s = self.direct_entry()
            else:
                s = self.no_ui()

            if s != None:
                self.send(s)

    def return_collected(self) -> list[str]: ...
    def rsync(self) -> None: ...
    def send(self, m: str) -> None: ...


class Wifi(Connection):
    def __init__(self):
        self.data: list[str]

    def start_connection(self) -> None:
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind the socket to a specific address and port
        self.s.bind((host_addr, so_port))
        self.s.listen(5)
        print(f"Listening on {rpi_addr}:{so_port}")
        c, c_address = self.s.accept()  # accept incoming connections
        self.c = c
        print(f"Accepted connection from {c_address[0]}:{c_address[1]}")
        self.t1 = threading.Thread(self.listen())

    def listen(self) -> None:
        self.live = True
        while self.live:
            m = self.recv()
            self.data.append(m)

    def return_collected(self) -> list[str]:
        d = self.data
        self.data.clear()
        return d

    def send(self, m: str) -> None:
        msg = m.encode(utf8)
        self.c.send(msg)

    def recv(self) -> str:
        msg_bytes = self.c.recv(so_msg_size)
        msg = msg_bytes.decode(utf8)
        return msg

    def close(self) -> None:
        self.s.close()
        self.c.close()

    def rsync(self) -> None:
        s = f"rsync -avz -e ssh {rpi_name}@{rpi_addr}:{rpi_data_path} {host_data_path}"
        print(s)
        os.system(s)


class Ethernet(Connection):
    def __init__(self):
        self.data: list[str]

    def start_connection(self) -> None:
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind the socket to a specific address and port
        self.s.bind((host_addr, so_port))
        self.s.listen(5)
        print(f"Listening on {rpi_hostname}:{so_port}")
        c, c_address = self.s.accept()  # accept incoming connections
        self.c = c
        print(f"Accepted connection from {c_address[0]}:{c_address[1]}")
        self.t1 = threading.Thread(self.listen())

    def listen(self) -> None:
        self.live = True
        while self.live:
            m = self.recv()
            self.data.append(m)

    def return_collected(self) -> list[str]:
        d = self.data
        self.data.clear()
        return d

    def send(self, m: str) -> None:
        msg = m.encode(utf8)
        self.c.send(msg)

    def recv(self) -> str:
        msg_bytes = self.c.recv(so_msg_size)
        msg = msg_bytes.decode(utf8)
        return msg

    def close(self) -> None:
        self.s.close()
        self.c.close()

    def rsync(self) -> None:
        s = f"rsync -avz -e ssh {rpi_name}@{rpi_hostname}:{rpi_data_path} {host_data_path}"
        print(s)
        os.system(s)


class Cellular(Connection):
    pass


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
    parser.add_argument(
        "-sync", "-s", action="store_true", help="sync data, no interface"
    )

    args = vars(parser.parse_args())  # get arguments from command line
    ui = args.get("ui")
    command = args.get("command")
    sync = args.get("sync")

    if isinstance(ui, bool) and ui:  # if user wants interface
        command = ui_commands.command_menu()  # get command from user
        global global_ui
        global_ui = True
    if command != None:  # if there's a command to send, send it
        conn = Connection()
        conn.send(command)
    elif sync:
        s = f"rsync -avz -e ssh {rpi_name}@{rpi_addr}:{rpi_data_path} {host_data_path}"
        print(s)
        os.system(s)
    else:
        conn = Connection()


if __name__ == "__main__":
    main()
