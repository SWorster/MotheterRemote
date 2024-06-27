import serial
import threading

"""
# addr = "/dev/tty.usbmodem578E0230291"
# BAUD = 115200
# s = serial.Serial(addr, BAUD, timeout=None)
# full_msg = s.read_until("\n".encode())
# msg = full_msg.decode().split("\n")[0]
# print(msg)
# s.close()
"""

BAUD = 115200
EOL = "\n"
EOF = "\r"


class Ser:
    def __init__(self, addr: str = "/dev/ttyUSB0"):
        self.addr = addr
        self.s = serial.Serial(addr, BAUD, timeout=None)
        self.t1 = threading.Thread(self.listen())
        self.t1.start()

    def send(self, msg: str | list[str] = "test") -> None:
        if isinstance(msg, list):
            m = EOL.join(msg)
        else:
            m = msg
        self.s.write((m + EOF).encode())
        if "close" in m:
            print("closing serial")
            self.s.close()
            exit()

    def listen(self) -> None:
        self.live = True
        while self.live:
            full_msg = self.s.read_until(EOF.encode())
            msg_arr = full_msg.decode().split(EOL)
            for msg in msg_arr:
                print(msg)

    def send_loop(self) -> None:
        while True:
            i = input("Send: ")
            self.send(i)

    def deafen(self) -> None:
        self.live = False


if __name__ == "__main__":
    s = Ser()
    s.send_loop()
