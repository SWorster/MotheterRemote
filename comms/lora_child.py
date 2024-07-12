"""
Runs on an accessory RPi that communicates to the main RPi using LoRa radio. This is not part of a relay: this RPi must be directly connected to the sensor.
"""

import time
import serial
import threading

# module imports
import configs
import sensor

ADDR = configs.acc_lora_port
BAUD = configs.BAUD
EOL = configs.EOL
EOF = configs.EOF
device_type = configs.device_type


class Ser:
    def __init__(self):
        """initialize serial connection to device"""
        self.s = serial.Serial(ADDR, BAUD, timeout=None)
        # self.device = sensor.SQM()  # initialize device
        if device_type == "SQM-LU":
            self.device = sensor.SQMLU()
        elif device_type == "SQM-LE":
            self.device = sensor.SQMLE()
        else:
            self.device = sensor.SQMLU()  # default
        self.device.start_continuous_read()  # start device listener
        time.sleep(1)
        self.radio = threading.Thread(target=self.listen_radio)  # run radio listener
        self.sensor = threading.Thread(target=self.listen_sensor)  # run sensor listener
        self.radio.start()
        self.sensor.start()

    def listen_radio(self) -> None:
        """get incoming radio messages, send them to device"""
        cur_thread = threading.current_thread()
        print("Radio listener running in thread:", cur_thread.name)
        self.live = True
        while self.live:
            time.sleep(1)
            full_msg = self.s.read_until(EOF.encode())
            msg_arr = full_msg.decode().split(EOL)
            for msg in msg_arr:
                time.sleep(0.1)
                m = msg.strip()
                print(f"Received over radio: {m}")
                self.device.rpi_to_client(m)  # send command

    def listen_sensor(self) -> None:
        """get incoming sensor messages, send them over radio"""
        cur_thread = threading.current_thread()
        print("Listener loop running in thread:", cur_thread.name)
        self.live = True
        while self.live:
            time.sleep(1)
            resp = self.device.client_to_rpi()  # get response from device
            if len(resp) != 0:
                print(f"Received from sensor: {resp}")
                self.send(resp)

    def send(self, msg: str | list[str] = "test") -> None:
        """send sensor responses to parent over radio

        Args:
            msg (str | list[str], optional): message(s) to send. Defaults to "test".
        """
        if isinstance(msg, list):
            m = EOL.join(msg)  # if list, collate into string
        else:
            m = msg
        print(f"Sending over radio: {m}")
        self.s.write((m + EOF).encode())

    def send_loop(self) -> None:
        """ui for debugging only"""
        while True:
            i = input("Send: ")
            self.send(i)


if __name__ == "__main__":
    s = Ser()
