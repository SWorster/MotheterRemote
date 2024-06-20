import socket
import sys
import serial
import time

address = "/dev/ttyUSB0"
port = 12345
_meta_len_ = None


def setup():
    s = socket.socket()
    host = socket.gethostname()
    s.bind((host, port))
    s.listen(5)
    # sensor = SQMLU()
    while True:
        c, addr = s.accept()
        print(f"Connected to {repr(addr[1])}")
        c.listen(5)

        msg = c.recv(1024).decode()
        # resp = sensor.send_command(msg)
        resp = "got " + msg

        s.send(resp.encode())


class SQMLU:
    """I shamelessly Frankenstein-ed this from PY3SQM. Just needed the serial connection to the sensor."""

    def __init__(self):
        """Search the photometer and read its metadata"""
        try:
            print(("Trying fixed device address %s ... " % str(address)))
            self.addr = address
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
        """Photometer search. Name of the port depends on the platform."""
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

    def send_command(self, command: str, tries: int = 1) -> str:
        """Read the serial number, firmware version"""
        print(".", end="")
        msg: str = ""
        self.s.write(f"{command}".encode())
        time.sleep(1)
        byte_msg = self.read_buffer()
        try:  # Sanity check
            assert byte_msg != None
            msg = byte_msg.decode()
            assert len(msg) == _meta_len_ or _meta_len_ == None
        except:
            if tries <= 0:
                print(("ERR. Reading the photometer!: %s" % str(byte_msg)))
                return ""
            time.sleep(1)
            self.reset_device()
            time.sleep(1)
            msg = self.send_command(command, tries - 1)
            print(("Sensor info: " + str(msg)), end=" ")
        return msg

    def read_data(self, tries: int = 1) -> str:
        return self.send_command("rx", tries)

    def read_metadata(self, tries: int = 1) -> str:
        return self.send_command("ix", tries)

    def read_calibration(self, tries: int = 1) -> str:
        return self.send_command("cx", tries)


setup()
