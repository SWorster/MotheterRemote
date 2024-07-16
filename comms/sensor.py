"""
Runs on the RPi that is directly connected to the sensor.
"""

import sys
import time
import struct
import socket
import serial
import argparse
import threading

# module import
import configs

# device info
device_type = configs.device_type.replace("_", "-")
device_addr = configs.device_addr

# debugging and retry settings
DEBUG = configs.debug
tries = configs.tries

# LU-specific
LU_BAUD = configs.LU_BAUD
lu_timeout = configs.LU_TIMEOUT

# LE-specific
LE_PORT = configs.LE_PORT
SOCK_BUF = configs.LE_SOCK_BUF
le_timeout = configs.LE_TIMEOUT

# text encoding
EOL = configs.EOL
utf8 = configs.utf8
hex = configs.hex

# timing
long_s = configs.long_s
mid_s = configs.mid_s
short_s = configs.short_s


if device_type == "SQM-LE":
    import socket
elif device_type == "SQM-LU":
    import serial


class SQM:
    """Shared methods for SQM devices"""

    def reset_device(self) -> None:
        """Connection reset"""
        self.close_connection()
        time.sleep(short_s)
        self.start_connection()

    def clear_buffer(self):
        """clears buffer and prints to console"""
        print("Clearing buffer ... | ", end="")
        print(self.read_buffer(), "| ... DONE")

    def send_and_receive(self, s: str, tries: int = tries) -> str:
        """sends and receives a single command. called from main

        Args:
            command (str): command to send
            tries (int, optional): how many attempts to make

        Returns:
            str: sensor response
        """
        m: str = ""
        self.send_command(s)
        time.sleep(long_s)
        byte_m = self.read_buffer()
        try:  # Sanity check
            assert byte_m != None
            m = byte_m.decode(utf8)
        except:
            if tries <= 0:
                print(("ERR. Reading the photometer!: %s" % str(byte_m)))
                if DEBUG:
                    raise
                return ""
            time.sleep(mid_s)
            self.reset_device()
            time.sleep(mid_s)
            m = self.send_and_receive(s, tries - 1)
            print(("Sensor info: " + str(m)), end=" ")
        return m

    def start_continuous_read(self) -> None:
        """starts listener"""
        self.data: list[str] = []
        self.live = True
        self.t1 = threading.Thread(target=self.listen)  # listener in background
        self.t1.start()

    def stop_continuous_read(self) -> None:
        """stops listener"""
        self.live = False
        self.t1.join()

    def listen(self):
        """listener. runs in dedicated thread"""
        self.live
        while self.live:
            time.sleep(short_s)
            self.read_buffer()  # this stores the data

    def return_collected(self) -> list[str]:
        """clears data array, returns contents

        Returns:
            list[str]: data to return
        """
        d = self.data[:]  # pass by value, not reference
        self.data.clear()
        return d

    def rpi_to_client(self, s: str) -> None:
        """sends a command to the sensor

        Args:
            s (str): command to send
        """
        print(f"Sending to sensor: {s}")
        self.send_command(s)

    def client_to_rpi(self) -> list[str]:
        """returns responses from sensor

        Returns:
            list[str]: responses
        """
        m_arr = self.return_collected()
        return m_arr

    def start_connection(self) -> None: ...

    def close_connection(self) -> None: ...

    def read_buffer(self) -> bytes | None: ...

    def send_command(self, s: str) -> None: ...


class SQMLE(SQM):
    """WARNING: this code hasn't been tested, because I don't have an SQM-LE to test with."""

    def __init__(self) -> None:
        """Search the photometer in the network and read its metadata"""
        self.data: list[str] = []
        try:
            self.addr = device_addr
            self.start_connection()
        except:
            print(
                f"Device not found on {device_addr}, searching for device address ..."
            )
            self.addr = self.search()
            print(("Found address %s ... " % str(self.addr)))
            self.start_connection()
        self.clear_buffer()

    def search(self) -> list[None] | str:
        """Search SQM LE in the LAN. Return its address"""
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setblocking(False)

        if hasattr(socket, "SO_BROADCAST"):
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # used to be decode, idk why, it needs to be bytes anyways
        self.s.sendto(
            "000000f6".encode(hex), ("255.255.255.255", 30718)
        )  # no idea why this port is used
        buf = ""
        starttime = time.time()

        print("Looking for replies; press Ctrl-C to stop.")
        addr = [None, None]
        while True:
            try:
                (buf, addr) = self.s.recvfrom(30)
                # BUG: the 3rd hex character probably doesn't correspond to the 3rd bytes character. However, I'm not working with an SQM-LE so I've made the command decision to ignore this.
                # was buf[3].decode("hex")
                if buf.decode(hex)[3] == "f7":
                    # was buf[24:30].encode("hex")
                    print("Received from %s: MAC: %s" % (addr, buf.decode(hex)[24:30]))
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
        self.s.settimeout(le_timeout)
        self.s.connect((self.addr, int(LE_PORT)))
        # self.s.settimeout(1) # idk why this was commented, I didn't comment it out

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
        m = None
        try:
            m = self.s.recv(SOCK_BUF)
            if m.decode(utf8) == "":
                return
            self.data.append(m.decode(utf8).strip())
        except:
            pass
        return m

    def send_command(self, s: str) -> None:
        """how the SQM_LE sends a command to the sensor

        Args:
            s (str): the command to send
        """
        self.s.send(s.encode(utf8))


class SQMLU(SQM):
    def __init__(self) -> None:
        """Search for the photometer and read its metadata"""
        self.data: list[str] = []
        try:
            print(f"Trying fixed device address {device_addr}")
            self.addr = device_addr
            # self.s = serial.Serial(self.addr, LU_BAUD, timeout=2)
            self.start_connection()
            print(f"Device found at address {device_addr}")

        except:  # device not at that address
            print(
                f"Device not found on {device_addr}, searching for device address ..."
            )
            self.addr = self.search()
            print(("Found address %s ... " % str(self.addr)))
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
            conn_test.write("ix".encode(utf8))
            if conn_test.readline().decode(utf8)[0] == "i":
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
        self.s = serial.Serial(self.addr, LU_BAUD, timeout=lu_timeout)

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
        m = None
        try:
            m = self.s.readline()
            if m.decode(utf8) == "":
                return
            self.data.append(m.decode(utf8).strip())
        except:
            pass
        return m

    def send_command(self, s: str) -> None:
        """how the SQM_LU sends a command to the sensor

        Args:
            s (str): the command to send
        """
        self.s.write(s.encode(utf8))

    def send_and_receive(self, s: str, tries: int = tries) -> str:
        m: str = ""
        self.send_command(s)
        time.sleep(long_s)
        byte_m = self.read_buffer()
        try:  # Sanity check
            assert byte_m != None
            m = byte_m.decode(utf8)
        except:
            if tries <= 0:
                print(("ERR. Reading the photometer!: %s" % str(byte_m)))
                if DEBUG:
                    raise
                return ""
            time.sleep(mid_s)
            self.reset_device()
            time.sleep(mid_s)
            m = self.send_and_receive(s, tries - 1)
            print(("Sensor info: " + str(m)), end=" ")
        return m


if __name__ == "__main__":
    """This file is designed to run only on the RPi that is directly hooked up to the sensor. If it is run as main, it will just parse your arguments and print the sensor response. To get multiple sensor responses, create an SQM() instance from another program."""
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
        print(f"Command is not a string. command: {command}, type: {type(command)}")
        exit()

    if device_type == "SQM-LU":
        d = SQMLU()
    elif device_type == "SQM-LE":
        d = SQMLE()
    else:
        d = SQMLU()  # default
    # d = SQM()  # create device
    time.sleep(long_s)
    resp = d.send_and_receive(command)
    print(f"Sensor response: {resp}")
