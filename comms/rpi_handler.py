import configs
import lora_parent
import sensor
import threading
import rpi_wifi

# import serial

radio = configs.rpi_is_radio
wifi = configs.rpi_is_wifi
cellular = configs.rpi_is_cellular
ADDR = configs.rpi_lora_port
BAUD = 115200
EOL = "\n"
EOF = "\r"


class Input:
    """interface for different host connections"""

    def __init__(self):
        if wifi:
            self = Wifi()
        elif cellular:
            self = Cellular()

    def host_to_rpi(self) -> str: ...

    def rpi_to_host(self, m: str): ...


class Wifi(Input):
    """handles wifi connection"""

    def __init__(self):
        self.conn = rpi_wifi.sock()

    def host_to_rpi(self) -> str:
        return self.conn.recv()

    def rpi_to_host(self, m: str):
        self.conn.send(m)


class Cellular(Input):
    """handles cellular connection"""

    def __init__(self):
        pass

    def host_to_rpi(self) -> str: ...

    def rpi_to_host(self, m: str): ...


class Output:
    """interface for output connections"""

    def __init__(self):
        if radio:
            self = Radio()
        else:
            self = Direct()

    def rpi_to_client(self, m: str): ...

    def client_to_rpi(self) -> str: ...


class Radio(Output):  # client = rpi over lora
    """handles radio connection"""

    def __init__(self):
        self.device = lora_parent.Ser()

    def rpi_to_client(self, m: str):
        self.device.send(m)

    def client_to_rpi(self) -> str:
        msg_arr = self.device.return_collected()
        return EOL.join(msg_arr)


class Direct(Output):  # in this case client=sensor
    """handles sensor connection"""

    def __init__(self):
        self.device = sensor.SQM()

    def rpi_to_client(self, m: str):
        self.device.send_command(m)

    def client_to_rpi(self) -> str:
        msg_arr = self.device.return_collected()
        return EOL.join(msg_arr)


class Handler(Input, Output):
    """the handler class. inherits methods from both input and output classes so that it can run everything"""

    def __init__(self):
        """start input/output listeners"""
        self.t1 = threading.Thread(self.listen_host())
        self.t2 = threading.Thread(self.listen_client())
        self.t1.start()
        self.t2.start()

    def listen_host(self) -> None:
        while True:
            m = self.host_to_rpi()
            self.rpi_to_client(m)

    def listen_client(self) -> None:
        while True:
            m = self.client_to_rpi()
            self.rpi_to_host(m)

    def host_to_rpi(self) -> str: ...
    def rpi_to_host(self, m: str): ...
    def client_to_rpi(self) -> str: ...
    def rpi_to_client(self, m: str): ...
