import serial
import threading
import configs

ADDR = configs.rpi_lora_port
BAUD = 115200
EOL = "\n"
EOF = "\r"


class Ser:
    def __init__(self):
        self.s = serial.Serial(ADDR, BAUD, timeout=None)
        self.t1 = threading.Thread(self.listen())  # listener in background
        # self.t1.start()

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
                print(msg)

    def send(self, msg: str | list[str] = "test") -> None:
        if isinstance(msg, list):
            m = EOL.join(msg)
        else:
            m = msg
        self.s.write((m + EOF).encode())

    def send_loop(self) -> None:  # ui for debugging only
        while True:
            i = input("Send: ")
            self.send(i)


if __name__ == "__main__":
    s = Ser()
    s.t1.start()
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
