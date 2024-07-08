"""
This handler runs on the main RPi, which is either directly connected to the sensor or is acting as a middleman for a radio-capable RPi. It
"""

import threading

# module imports
import configs
import rpi_wifi
import lora_parent
import sensor

radio = configs.rpi_is_radio
wifi = configs.rpi_is_wifi
cellular = configs.rpi_is_cellular
ADDR = configs.rpi_lora_port
BAUD = configs.BAUD
EOL = configs.EOL
EOF = configs.EOF


class Input:
    """interface for different host connections"""

    def __init__(self):
        if wifi:
            self = Wifi()
        elif cellular:
            self = Cellular()

    def host_to_rpi(self) -> str: ...

    def rpi_to_host(self, m: str) -> None: ...


class Wifi(Input):
    """handles wifi connection"""

    def __init__(self):
        self.conn = rpi_wifi.sock()

    def host_to_rpi(self) -> str:
        return self.conn.recv()

    def rpi_to_host(self, m: str) -> None:
        self.conn.send(m)


class Cellular(Input):
    """handles cellular connection"""

    def __init__(self):
        pass

    def host_to_rpi(self) -> str: ...

    def rpi_to_host(self, m: str) -> None: ...


class Output:
    """interface for output connections"""

    def __init__(self):
        if radio:
            self = Radio()
        else:
            self = Direct()

    def rpi_to_client(self, m: str) -> None: ...

    def client_to_rpi(self) -> str: ...


class Radio(Output):  # client = rpi over lora
    """handles radio connection"""

    def __init__(self):
        self.device = lora_parent.Ser()

    def rpi_to_client(self, m: str) -> None:
        self.device.send(m)

    def client_to_rpi(self) -> str:
        msg_arr = self.device.return_collected()
        return EOL.join(msg_arr)


class Direct(Output):  # in this case client=sensor
    """handles sensor connection"""

    def __init__(self):
        self.device = sensor.SQM()

    def rpi_to_client(self, m: str) -> None:
        self.device.send_command(m)

    def client_to_rpi(self) -> str:
        msg_arr = self.device.return_collected()
        return EOL.join(msg_arr)


class Handler(Input, Output):
    """the handler class. inherits methods from both input and output classes so that it can run everything"""

    def __init__(self):
        """start input/output listeners"""
        self.t1 = threading.Thread(target=self.listen_host)
        self.t2 = threading.Thread(target=self.listen_client)
        self.t1.start()
        self.t2.start()

    def listen_host(self) -> None:
        print("listening for messages from host")
        while True:
            m = self.host_to_rpi()
            self.rpi_to_client(m)

    def listen_client(self) -> None:
        print("listening for messages from client")
        while True:
            m = self.client_to_rpi()
            self.rpi_to_host(m)

    def host_to_rpi(self) -> str: ...
    def rpi_to_host(self, m: str) -> None: ...
    def client_to_rpi(self) -> str: ...
    def rpi_to_client(self, m: str) -> None: ...


def main():
    print("here")
    h = Handler()
    print(f"started handler {h}")


if __name__ == "__main__":
    main()
