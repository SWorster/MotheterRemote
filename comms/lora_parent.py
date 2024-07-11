"""
Handles LoRa communications from main RPi.
"""

import serial
import threading

# module imports
import configs

ADDR = configs.rpi_lora_port
BAUD = configs.BAUD
EOL = configs.EOL
EOF = configs.EOF


class Radio:
    def __init__(self):
        self.data: list[str]
        self.s = serial.Serial(ADDR, BAUD, timeout=None)
        self.t1 = threading.Thread(target=self.start_listen)  # listener in background
        self.t1.daemon = True
        self.t1.start()

    def start_listen(self) -> None:
        try:
            self.t1.start()
        except RuntimeError:
            print("already running listen()")

    def listen(self) -> None:
        self.live = True
        while self.live:
            full_msg = self.s.read_until(EOF.encode())
            msg_arr = full_msg.decode().split(EOL)
            for msg in msg_arr:
                self.data.append(msg)

    def send(self, msg: str | list[str] = "test") -> None:
        if isinstance(msg, list):
            m = EOL.join(msg)
        else:
            m = msg
        self.s.write((m + EOF).encode())

    def return_collected(self) -> list[str]:
        d = self.data
        self.data.clear()
        return d

    def send_loop(self) -> None:  # ui for debugging only
        while True:
            i = input("Send: ")
            self.send(i)

    def rpi_to_client(self, m: str) -> None:
        self.send(m)

    def client_to_rpi(self) -> str:
        msg_arr = self.return_collected()
        return EOL.join(msg_arr)


if __name__ == "__main__":
    s = Radio()
    # s.t1.start()
    s.send_loop()


"""
# addr = "/dev/tty.usbmodem578E0230291"
# BAUD = 115200
# s = serial.Serial(addr, BAUD, timeout=None)
# full_msg = s.read_until("\n".encode())
# msg = full_msg.decode().split("\n")[0]
# print(msg)
# s.close()
"""
"""
        if "close" in m:
            print("closing serial")
            self.live = False  # kills listener
            self.s.close()  # closes port
            exit()
            """
