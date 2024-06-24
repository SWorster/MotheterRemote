import os  # type: ignore
import sys
import time
import struct
import socket
import serial
import configs


# config imports
device_type = configs.device_type
device_addr = configs.device_addr
device_id = configs.device_id
DEBUG = configs.debug

# constants
LU_BAUD = 115200
LE_PORT = 10001
SOCK_BUF = 256
_meta_len_ = None  # Default, to ignore the length of the read string.


def relaxed_import(themodule: str) -> None:
    try:
        exec("import " + str(themodule))
    except:
        pass


# If the old format (SQM_LE/SQM_LU) is used, replace _ with -
device_type = device_type.replace("_", "-")

if device_type == "SQM-LE":
    import socket
elif device_type == "SQM-LU":
    import serial


class SQM:
    def read_data(self, tries: int = 1) -> str:
        return ""

    def read_photometer(self, Nmeasures: int = 1, PauseMeasures: int = 2) -> str:
        # Get the raw data from the photometer and process it.
        raw_data = self.read_data(tries=10)

        # Just to show on screen that the program is alive and running
        sys.stdout.write(".")
        sys.stdout.flush()
        return raw_data

    def remove_linebreaks(self, data: str) -> str:
        # Remove line breaks from data
        data = data.replace("\r\n", "")
        data = data.replace("\r", "")
        data = data.replace("\n", "")
        return data

    def format_value(self, data: str, remove_str: str = " ") -> str:
        # Remove string and spaces from data
        data = self.remove_linebreaks(data)
        data = data.replace(remove_str, "")
        data = data.replace(" ", "")
        return data

    def metadata_process(self, msg: str, sep: str = ",") -> None:
        # Separate the output array in items
        msg = self.format_value(msg)
        msg_array = msg.split(sep)

        # Get Photometer identification codes
        self.protocol_number = int(self.format_value(msg_array[1]))
        self.model_number = int(self.format_value(msg_array[2]))
        self.feature_number = int(self.format_value(msg_array[3]))
        self.serial_number = int(self.format_value(msg_array[4]))

    def start_connection(self):
        """Start photometer connection"""
        pass

    def close_connection(self):
        """End photometer connection"""
        pass

    def reset_device(self):
        """Restart connection"""
        self.close_connection()
        time.sleep(0.1)
        self.start_connection()


class SQMLE(SQM):
    def __init__(self):
        """
        Search the photometer in the network and
        read its metadata
        """
        try:
            print(("Trying fixed device address %s ... " % str(device_addr)))
            self.addr = device_addr
            self.port = 10001
            self.start_connection()
        except:
            print("Trying auto device address ...")
            self.addr = self.search()
            print(("Found address %s ... " % str(self.addr)))
            self.port = 10001
            self.start_connection()

        # Clearing buffer
        print(("Clearing buffer ... |"), end=" ")
        buffer_data = self.read_buffer()
        print((buffer_data), end=" ")
        print("| ... DONE")
        print("Reading test data (ix,cx,rx)...")
        time.sleep(1)
        self.ix_readout = self.read_metadata(tries=10)
        time.sleep(1)
        self.cx_readout = self.read_calibration(tries=10)
        time.sleep(1)
        self.rx_readout = self.read_data(tries=10)

    def search(self):
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
            return addr[0]

    def start_connection(self) -> None:
        """Start photometer connection"""
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(20)
        self.s.connect((self.addr, int(self.port)))
        # self.s.settimeout(1)

    def close_connection(self) -> None:
        """End photometer connection"""
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))

        # Check until there is no answer from device
        request = ""
        r = True
        while r:
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

    def reset_device(self) -> None:
        """Connection reset"""
        # print('Trying to reset connection')
        self.close_connection()
        self.start_connection()

    def read_something(self, tries: int = 1, letter: str = "r") -> str:
        """Read the serial number, firmware version"""
        msg: str = ""
        self.s.send(f"{letter}x".encode())
        time.sleep(1)
        byte_msg = self.read_buffer()
        try:  # Sanity check
            assert byte_msg != None
            msg = byte_msg.decode()
            assert len(msg) == _meta_len_ or _meta_len_ == None
            assert letter in msg
            self.metadata_process(msg)
        except:
            if tries <= 0:
                print(("ERR. Reading the photometer!: %s" % str(byte_msg)))
                if DEBUG:
                    raise
                return ""
            time.sleep(1)
            self.reset_device()
            time.sleep(1)
            msg = self.read_something(tries - 1, letter)
            print(("Sensor info: " + str(msg)), end=" ")
        return msg

    def read_data(self, tries: int = 1) -> str:
        return self.read_something(tries, "r")

    def read_metadata(self, tries: int = 1) -> str:
        return self.read_something(tries, "i")

    def read_calibration(self, tries: int = 1) -> str:
        return self.read_something(tries, "c")


class SQMLU(SQM):
    def __init__(self):
        """
        Search the photometer and
        read its metadata
        """

        try:
            print(("Trying fixed device address %s ... " % str(device_addr)))
            self.addr = device_addr
            self.bauds = 115200
            self.start_connection()
        except:
            print("Trying auto device address ...")
            self.addr = self.search()
            print(("Found address %s ... " % str(self.addr)))
            self.bauds = 115200
            self.start_connection()

        # Clearing buffer
        print(("Clearing buffer ... |"), end=" ")
        buffer_data = self.read_buffer()
        print((buffer_data), end=" ")
        print("| ... DONE")
        print("Reading test data (ix,cx,rx)...")
        time.sleep(1)
        self.ix_readout = self.read_metadata(tries=10)
        time.sleep(1)
        self.cx_readout = self.read_calibration(tries=10)
        time.sleep(1)
        self.rx_readout = self.read_data(tries=10)

    def search(self):
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
            conn_test = serial.Serial(port, 115200, timeout=1)
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

    def start_connection(self):
        """Start photometer connection"""

        self.s = serial.Serial(self.addr, 115200, timeout=2)

    def close_connection(self):
        """End photometer connection"""
        # Check until there is no answer from device
        request = ""
        r = True
        while r:
            r = self.read_buffer()
            request += str(r)

        self.s.close()

    def reset_device(self):
        """Connection reset"""
        # print('Trying to reset connection')
        self.close_connection()
        self.start_connection()

    def read_buffer(self):
        """Read the data"""
        msg = None
        try:
            msg = self.s.readline()
        except:
            pass
        return msg

    def read_something(self, tries: int = 1, letter: str = "r") -> str:
        """Read the serial number, firmware version"""
        msg: str = ""
        self.s.write(f"{letter}x".encode())
        time.sleep(1)
        byte_msg = self.read_buffer()
        try:  # Sanity check
            assert byte_msg != None
            msg = byte_msg.decode()
            assert len(msg) == _meta_len_ or _meta_len_ == None
            assert letter in msg
            self.metadata_process(msg)
        except:
            if tries <= 0:
                print(("ERR. Reading the photometer!: %s" % str(byte_msg)))
                if DEBUG:
                    raise
                return ""
            time.sleep(1)
            self.reset_device()
            time.sleep(1)
            msg = self.read_something(tries - 1, letter)
            print(("Sensor info: " + str(msg)), end=" ")
        return msg

    def read_data(self, tries: int = 1) -> str:
        return self.read_something(tries, "r")

    def read_metadata(self, tries: int = 1) -> str:
        return self.read_something(tries, "i")

    def read_calibration(self, tries: int = 1) -> str:
        return self.read_something(tries, "c")
