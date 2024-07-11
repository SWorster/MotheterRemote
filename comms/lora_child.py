"""
Runs on an accessory RPi that communicates to the main RPi using LoRa radio. This is not part of a relay: this RPi must be directly connected to the sensor.
"""

import serial
import threading

# module imports
import configs
import sensor

ADDR = configs.acc_lora_port
BAUD = configs.BAUD
EOL = configs.EOL
EOF = configs.EOF


class Ser:
    def __init__(self):
        """initialize serial connection to device"""
        self.s = serial.Serial(ADDR, BAUD, timeout=None)
        self.t1 = threading.Thread(target=self.listen)  # run listener in background
        # self.t1.daemon = True
        self.t1.start()
        self.device = sensor.SQM()  # initialize device

    def listen(self) -> None:
        """get incoming radio messages, send them to device"""
        self.live = True
        while self.live:
            full_msg = self.s.read_until(EOF.encode())
            msg_arr = full_msg.decode().split(EOL)
            for msg in msg_arr:
                resp = self.device.send_and_receive(msg)  # get response from device
                self.send(resp)  # forward response over radio

    def send(self, msg: str | list[str] = "test") -> None:
        """send sensor responses to parent over radio

        Args:
            msg (str | list[str], optional): message(s) to send. Defaults to "test".
        """
        if isinstance(msg, list):
            m = EOL.join(msg)  # if list, collate into string
        else:
            m = msg
        self.s.write((m + EOF).encode())

    def send_loop(self) -> None:  # ui for debugging only
        while True:
            i = input("Send: ")
            self.send(i)


if __name__ == "__main__":
    s = Ser()
    # s.send_loop()


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
