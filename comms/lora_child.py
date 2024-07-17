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

echo = True  # print to log file


class Ser:
    """serial connection for radio"""

    def __init__(self):
        """initialize serial connection to device"""
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
        time.sleep(mid_s)
        self.radio = threading.Thread(target=self._listen_radio)  # run radio listener
        self.sensor = threading.Thread(
            target=self._listen_sensor
        )  # run sensor listener
        self.radio.start()
        self.sensor.start()

    def _listen_radio(self) -> None:
        """get incoming radio messages, send them to device"""
        cur_thread = threading.current_thread()
        p(f"Radio listener running in {cur_thread.name}")
        self.live = True
        while self.live:
            time.sleep(mid_s)
            full_msg = self.s.read_until(EOF.encode(utf8))
            msg_arr = full_msg.decode(utf8).split(EOL)
            for msg in msg_arr:
                time.sleep(short_s)
                m = msg.strip()
                p(f"Received over radio: {m}")
                if "rsync" in m:
                    self._rsync(m)
                else:
                    self.device.rpi_to_client(m)  # send command

    def _listen_sensor(self) -> None:
        """get incoming sensor messages, send them over radio"""
        cur_thread = threading.current_thread()
        p(f"Listener loop running in {cur_thread.name}")
        self.live = True
        while self.live:
            time.sleep(mid_s)
            resp = self.device.client_to_rpi()  # get response from device
            if len(resp) != 0:
                p(f"Received from sensor: {resp}")
                self._send(resp)

    def _send(self, msg: str | list[str] = "test") -> None:
        """send sensor responses to parent over radio

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
        """ui for debugging only"""
        while True:
            i = input("Send: ")
            self._send(i)

    def _rsync(self, s: str) -> None:
        """handles rsync requests

        Args:
            s (str): request to handle
        """
        p("Handling rsync")
        if "list" in s:
            p("Sending file list")
            self._send(self._get_file_list())
        else:  # must be asking for specific file
            p("getting file...")
            name = s.replace("rsync ", "").strip()  # rest of request is path
            if not os.path.isfile(name):  # if wrong, ignore
                p(f"path {name} not found")
            p(f"sending file {name}")

            first = f"rsync {name}{EOL}"
            middle = open(name, "r").read()
            last = EOF

            message = first + middle + last
            p(message)
            self.s.write(message.encode(utf8))

            # b = bytearray(f"rsync {name}{EOL}", utf8)  # prepend file name
            # p(f"b1: {b.decode()}")
            # file = bytearray(open(name, "rb").read())  # bytearray of file
            # b.extend(file)
            # p(f"b2: {b.decode()}")
            # b.extend(EOF.encode(utf8))  # EOF to finish
            # p(f"b3: {b.decode()}")

            # self.s.write(b)  # send bytearray
            # self.s.write(open(name, "rb").read())  # send as bytes

    def _get_file_list(self) -> str:
        """gets string list of all .dat files in the data directory on this rpi, with the corresponding date of modification

        Returns:
            str: name and modified date for each file, concatenated
        """

        def _all_file_list(path: str = "") -> list[str]:
            """recursively finds all .dat files in the rpi data directory.

            Args:
                path (str, optional): current path to search. Defaults to current working directory.

            Returns:
                list[str]: all .dat files in current directory
            """
            to_return: list[str] = []
            try:
                file_list = os.listdir(path)
            except:
                print(f"cannot find directory {path}, returning")
                return []
            for entry in file_list:
                p(f"{path}  /  {entry}")
                fullPath = os.path.join(path, entry)
                if os.path.isdir(fullPath):
                    to_return.extend(_all_file_list(fullPath))
                if fullPath.endswith(".dat"):
                    to_return.append(fullPath)
            p(str(to_return))
            return to_return

        l = _all_file_list(acc_data_path)
        a: list[str] = []
        a.append("rsync files")  # prepend header for parent processing
        p(str(l))
        for file in l:
            if file.endswith(".dat"):  # filter for dat files
                ctime = os.path.getmtime(file)  # seconds since 1970
                s = f"{file};{ctime}"  # entry with name and time
                a.append(s)
        c = str(a)
        p(f"TO SEND: {c}")
        return c


def p(s: str) -> None:
    global echo
    if echo:
        os.system(f"echo {s}")
    else:
        print(s, flush=True)  # print, even if in thread


if __name__ == "__main__":
    s = Ser()
