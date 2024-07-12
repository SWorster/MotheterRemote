"""
Handles LoRa communications from main RPi.
"""

import time
import serial
import threading

import configs

# radio connection
ADDR = configs.R_ADDR
BAUD = configs.R_BAUD

# text encoding
EOL = configs.EOL
EOF = configs.EOF
utf8 = configs.utf8

# timing
long_s = configs.long_s
mid_s = configs.mid_s
short_s = configs.short_s


class Radio:
    def __init__(self):
        self.data: list[str] = []
        self.s = serial.Serial(ADDR, BAUD, timeout=None)
        self.t1 = threading.Thread(target=self.start_listen)  # listener in background
        self.t1.daemon = True
        self.t1.start()

    def start_listen(self) -> None:
        """tries to start listener, if not already running"""
        try:
            self.t1.start()
        except RuntimeError:
            print("Listener already running")

    def listen(self) -> None:
        """radio listener that runs continuously"""
        self.live = True
        while self.live:
            time.sleep(short_s)
            full_msg = self.s.read_until(EOF.encode(utf8))
            msg_arr = full_msg.decode(utf8).split(EOL)
            for msg in msg_arr:
                print(f"Received over radio: {msg}")
                self.data.append(msg)

    def send(self, msg: str | list[str] = "rx") -> None:
        """sends message to child rpi over radio

        Args:
            msg (str | list[str], optional): message to send. Defaults to "rx".
        """
        if isinstance(msg, list):
            m = EOL.join(msg)
        else:
            m = msg
        self.s.write((m + EOF).encode(utf8))

    def return_collected(self) -> list[str]:
        d = self.data[:]  # pass by value, not reference
        self.data.clear()
        return d

    def send_loop(self) -> None:
        """ui for debugging only"""
        while True:
            i = input("Send: ")
            self.send(i)

    def rpi_to_client(self, m: str) -> None:
        print(f"Sending to radio: {m}")
        self.send(m)

    def client_to_rpi(self) -> str:
        msg_arr = self.return_collected()
        if len(msg_arr) != 0:
            print(f"Received over radio: {msg_arr}")
        return EOL.join(msg_arr)


if __name__ == "__main__":
    s = Radio()
    s.send_loop()
