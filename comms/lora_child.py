"""
Runs on an accessory RPi that communicates to the main RPi using LoRa radio. This RPi must be directly connected to the sensor.
"""

import time
import serial
import threading
import os

# module imports
import configs
import sensor

# where to store data
acc_data_path = configs.acc_data_path

# radio connection
ADDR = configs.R_ADDR
BAUD = configs.R_BAUD

# text encoding
EOL = configs.EOL
EOF = configs.EOF
utf8 = configs.utf8

# device info
device_type = configs.device_type

# timing
long_s = configs.long_s
mid_s = configs.mid_s
short_s = configs.short_s


class Ser:
    """Serial connection for radio"""

    def __init__(self):
        """Initialize serial connection to device"""
        self.s = serial.Serial(ADDR, BAUD, timeout=None)
        try:
            if device_type == "SQM-LU":
                self.device = sensor.SQMLU()
            elif device_type == "SQM-LE":
                self.device = sensor.SQMLE()
            else:
                self.device = sensor.SQMLU()  # default
        except Exception as e:
            p(f"{e}")  # if device not connected, quit
            exit()
        self.device.start_continuous_read()  # start device listener
        time.sleep(mid_s)  # wait for setup
        self.radio = threading.Thread(target=self._listen_radio)  #  radio listener
        self.sensor = threading.Thread(target=self._listen_sensor)  #  sensor listener
        self.radio.start()
        self.sensor.start()

    def _listen_radio(self) -> None:
        """Get incoming radio messages, send them to device"""
        p(f"Radio listener running in {threading.current_thread().name}")
        while True:
            try:
                time.sleep(mid_s)  # wait
                full_msg = self.s.read_until(EOF.encode(utf8))  # get message
                msg_arr = full_msg.decode(utf8).split(EOL)  # decode and split

                for msg in msg_arr:  # go through each message
                    time.sleep(short_s)
                    m = msg.strip()  # strip whitespace
                    p(f"Received over radio: {m}")
                    if "rsync" in m:
                        self._rsync(m)  # deal with rsync
                    else:
                        self.device.rpi_to_client(m)  # send command
            except Exception as e:
                print(e)

    def _listen_sensor(self) -> None:
        """Get incoming sensor messages, send them over radio"""
        p(f"Listener loop running in {threading.current_thread().name}")
        while True:
            time.sleep(mid_s)
            resp = self.device.client_to_rpi()  # get response from device
            if len(resp) != 0:  # if response has data
                p(f"Received from sensor: {resp}")
                self._send(resp)

    def _send(self, msg: str | list[str] = "test") -> None:
        """Send sensor responses to parent over radio

        Args:
            msg (str | list[str], optional): message(s) to send. Defaults to "test".
        """
        if isinstance(msg, list):
            m = EOL.join(msg)  # if list, collate into string
        else:
            m = msg
        p(f"Sending over radio: {m}")
        self.s.write((m + EOF).encode(utf8))

    def _send_loop(self) -> None:
        """Ui for debugging only. Sends message over radio"""
        while True:
            i = input("Send: ")
            self._send(i)

    def _rsync(self, s: str) -> None:
        """Handles rsync requests

        Args:
            s (str): request to handle
        """
        p("Handling rsync")
        if "list" in s:  # file list requested
            p("Sending file list")
            self._send(self._get_file_list())
        else:  # must be asking for specific file
            name = s.replace("rsync ", "").strip()  # rest of request is path
            if not os.path.isfile(name):  # if wrong, ignore
                p(f"Path {name} not found")
                return

            p(f"Reading file {name}")
            short = name.rfind("/")  # find where name starts at right of path
            short_name = name[short + 1 :]  # get name
            b = bytearray(f"rsync {short_name} {EOL}", utf8)  # prepend file name

            with open(name, "rb") as file:
                text = file.read()  # get text from file as bytes
                b.extend(text)  # append to bytearray
                b.extend(EOF.encode(utf8))  # EOF to finish
                p(f"File to send: {b.decode()}")

            self.s.write(b)  # send bytearray

    def _get_file_list(self) -> str:
        """Gets string list of all .dat files in the data directory on this RPi, with the corresponding date of modification

        Returns:
            str: name and modified date for each file, concatenated
        """

        def _all_file_list(path: str = "") -> list[str]:
            """Recursively finds all .dat files in the RPi data directory.

            Args:
                path (str, optional): current path to search. Defaults to current working directory.

            Returns:
                list[str]: all .dat files in current directory
            """
            to_return: list[str] = []
            try:
                file_list = os.listdir(path)  # get list of files
            except:
                print(f"Cannot find directory {path}, returning")
                return []  # something went wrong, stop recursing

            for entry in file_list:
                fullPath = os.path.join(path, entry)
                if os.path.isdir(fullPath):  # if directory, recurse on it
                    to_return.extend(_all_file_list(fullPath))
                if fullPath.endswith(".dat"):  # if .dat file, add to list
                    to_return.append(fullPath)
            return to_return

        l = _all_file_list(acc_data_path)
        a: list[str] = []
        a.append("rsync files")  # prepend header for parent processing
        for file in l:
            if file.endswith(".dat"):  # filter for dat files
                ctime = os.path.getmtime(file)  # seconds since 1970
                s = f"{file};{ctime}"  # entry with name and time
                a.append(s)
        c = str(a)  # convert array to string
        p(f"TO SEND: {c}")
        return c


def p(s: str) -> None:
    """Flushes buffer and prints. Enables print in threads

    Args:
        s (str): string to print
    """
    print(s, flush=True)


if __name__ == "__main__":
    p("\n\n")
    s = Ser()
