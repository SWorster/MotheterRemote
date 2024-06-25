import os  # type: ignore
import sys
import time
import struct
import socket
import serial
import configs
import argparse


# config imports
device_type = configs.device_type.replace("_", "-")
device_addr = configs.device_addr
DEBUG = configs.debug
host_addr = configs.host_addr
host_name = configs.host_name


# constants
LU_BAUD = 115200
LE_PORT = 10001
SOCK_BUF = 256
# _meta_len_ = None  # Default, to ignore the length of the read string.


if device_type == "SQM-LE":
    import socket
elif device_type == "SQM-LU":
    import serial


class SQM:
    """Shared methods for SQM devices"""

    def start_connection(self) -> None:
        """Start photometer connection"""
        pass

    def close_connection(self) -> None:
        """End photometer connection"""
        pass

    def reset_device(self) -> None:
        """Connection reset"""
        self.close_connection()
        time.sleep(0.1)
        self.start_connection()

    def clear_buffer(self):
        buffer_data = self.read_buffer()
        s = "Clearing buffer ... | " + str(buffer_data) + " | ... DONE"
        if s != "Clearing buffer ... | b'' | ... DONE":
            print(s)

    def read_buffer(self) -> bytes | None:
        pass

    def how_to_send(self, command: str) -> None:
        pass

    def send_command(self, command: str, tries: int = 3) -> str:
        msg: str = ""
        self.how_to_send(command)
        time.sleep(1)
        byte_msg = self.read_buffer()
        try:  # Sanity check
            assert byte_msg != None
            msg = byte_msg.decode()
        except:
            if tries <= 0:
                print(("ERR. Reading the photometer!: %s" % str(byte_msg)))
                if DEBUG:
                    raise
                return ""
            time.sleep(1)
            self.reset_device()
            time.sleep(1)
            msg = self.send_command(command, tries - 1)
            print(("Sensor info: " + str(msg)), end=" ")
        return msg


class SQMLE(SQM):
    """WARNING: this code hasn't been tested, because I don't have an SQM-LE to test with."""

    def __init__(self) -> None:
        """Search the photometer in the network and read its metadata"""
        try:
            self.addr = device_addr
        except:
            print(
                f"Device not found on {device_addr}, searching for device address ..."
            )
            self.addr = self.search()
            print(("Found address %s ... " % str(self.addr)))
        self.port = LE_PORT
        self.start_connection()

        self.clear_buffer()

    def search(self) -> list[None] | str:
        """Search SQM LE in the LAN. Return its address"""
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setblocking(False)

        if hasattr(socket, "SO_BROADCAST"):
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # used to be decode, idk why, it needs to be bytes anyways
        self.s.sendto("000000f6".encode("hex"), ("255.255.255.255", 30718))
        buf = ""
        starttime = time.time()

        print("Looking for replies; press Ctrl-C to stop.")
        addr = [None, None]
        while True:
            try:
                (buf, addr) = self.s.recvfrom(30)
                # BUG: the 3rd hex character probably doesn't correspond to the 3rd bytes character. However, I'm not working with an SQM-LE so I've made the command decision to ignore this.
                # was buf[3].decode("hex")
                if buf.decode("hex")[3] == "f7":
                    # was buf[24:30].encode("hex")
                    print(
                        "Received from %s: MAC: %s" % (addr, buf.decode("hex")[24:30])
                    )
            except:
                # Timeout in seconds. Allow all devices time to respond
                if time.time() - starttime > 3:
                    break
                pass

        try:
            assert addr[0] != None
        except:
            print("ERR. Device not found!")
            raise
        else:
            return str(addr[0])  # was addr[0]

    def start_connection(self) -> None:
        """Start photometer connection"""
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(20)
        self.s.connect((self.addr, int(self.port)))
        # self.s.settimeout(1) # idk why this is commented

    def close_connection(self) -> None:
        """End photometer connection"""
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))

        request = ""
        r = True
        while r:  # wait until device stops responding
            r = self.read_buffer()
            request += str(r)
        self.s.close()

    def read_buffer(self) -> bytes | None:
        """Read the data"""
        msg = None
        try:
            msg = self.s.recv(SOCK_BUF)
        except:
            pass
        return msg

    def how_to_send(self, command: str) -> None:
        """how the SQM_LE sends a command to the sensor

        Args:
            command (str): the command to send
        """
        self.s.send(command.encode())


class SQMLU(SQM):
    def __init__(self) -> None:
        """Search for the photometer and read its metadata"""
        try:
            self.addr = device_addr
        except:  # device not at that address
            print(
                f"Device not found on {device_addr}, searching for device address ..."
            )
            self.addr = self.search()
            print(("Found address %s ... " % str(self.addr)))
        self.bauds = LU_BAUD
        self.start_connection()
        self.clear_buffer()

    def search(self) -> str:
        """
        Photometer search.
        Name of the port depends on the platform.
        """
        ports_unix = ["/dev/ttyUSB" + str(num) for num in range(100)]
        ports_win = ["COM" + str(num) for num in range(100)]

        os_in_use = sys.platform
        ports: list[str] = []
        if os_in_use == "linux2":
            print("Detected Linux platform")
            ports = ports_unix
        elif os_in_use == "win32":
            print("Detected Windows platform")
            ports = ports_win

        used_port = None
        for port in ports:
            conn_test = serial.Serial(port, LU_BAUD, timeout=1)
            conn_test.write("ix".encode())
            # was conn_test.readline()[0] == "i"
            if conn_test.readline().decode()[0] == "i":
                used_port = port
                break

        try:
            assert used_port != None
        except:
            print("ERR. Device not found!")
            raise
        else:
            return used_port

    def start_connection(self) -> None:
        """Start photometer connection"""
        self.s = serial.Serial(self.addr, LU_BAUD, timeout=2)

    def close_connection(self) -> None:
        """End photometer connection"""
        request = ""
        r = True
        while r:  # wait until device stops responding
            r = self.read_buffer()
            request += str(r)
        self.s.close()

    def read_buffer(self) -> bytes | None:
        """Read the data"""
        msg = None
        try:
            msg = self.s.readline()
        except:
            pass
        return msg

    def how_to_send(self, command: str) -> None:
        """how the SQM_LU sends a command to the sensor

        Args:
            command (str): the command to send
        """
        self.s.write(command.encode())


def to_sensor(command: str) -> str:
    """Sends a command to the sensor and returns the sensor's response

    Args:
        command (str): command for sensor

    Returns:
        str: sensor's response
    """
    r = None
    if device_type == "SQM-LU":
        d = SQMLU()
        r = d.send_command(command)
    if device_type == "SQM-LE":
        d = SQMLE()
        r = d.send_command(command)

    if isinstance(r, str):
        return r
    return ""


if __name__ == "__main__":
    """This file is designed to run only on the RPi that is directly hooked up to the sensor. If it is run as main, it will just parse your arguments and print the sensor response."""
    parser = argparse.ArgumentParser(
        prog="rpi_to_sensor.py",
        description="Sends a command to the sensor. If run as main, prints result.",
        epilog=f"If no argument given, runs user interface",
    )

    parser.add_argument(
        "command",
        nargs="?",
        type=str,
        help="To send a command you've already made, just give it as an argument",
    )
    args = vars(parser.parse_args())
    command = args.get("command")
    if not isinstance(command, str):
        print("command is not a string. command:", command)
        exit()

    r = to_sensor(command)
    print(f"Sensor response: {r}")
    # if r != "":
    #     s = f"ssh {host_name}@{host_addr} 'echo {r}'"
    #     print(s)
    #     os.system(s)
