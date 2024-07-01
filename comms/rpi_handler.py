import configs

# import lora_parent
import sensor
import threading
import serial

radio = configs.rpi_is_radio
wifi = configs.rpi_is_wifi
cellular = configs.rpi_is_cellular
ADDR = configs.rpi_lora_port
BAUD = 115200
EOL = "\n"
EOF = "\r"


class Input:
    def __init__(self):
        if wifi:
            self = Wifi()
        elif cellular:
            self = Cellular()

    def send_to_host(self, m: str): ...


class Wifi(Input): ...


class Cellular(Input): ...


class Output:
    def __init__(self):
        if radio:
            self = Radio()
        else:
            self = Direct()

    def rpi_to_client(self, m: str): ...

    def client_to_rpi(self, m: str | None = None) -> str: ...


class Radio(Output):  # client = rpi over lora
    def __init__(self):
        self.s = serial.Serial(ADDR, BAUD, timeout=None)
        self.t1 = threading.Thread(self.listen())  # listener in background

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
                self.client_to_rpi(msg)

    def send(self, msg: str | list[str] = "test") -> None:
        if isinstance(msg, list):
            m = EOL.join(msg)
        else:
            m = msg
        self.s.write((m + EOF).encode())

    def rpi_to_client(self, m: str):
        self.send(m)

    def client_to_rpi(self, m: str | None = None) -> str: ...


class Direct(Output):  # in this case client=sensor
    def __init__(self):
        self.device = sensor.SQM()

    def rpi_to_client(self, m: str):
        resp = self.device.send_command(m)
        self.client_to_rpi(resp)

    def client_to_rpi(self, m: str | None = None) -> str:
        # because this is always/only triggered when we send a message to the sensor, we need to just return the string we get from the rpi_to_client function. the only reason this is so weird is because it needs to cooperate with the class it inherits from
        if m != None:
            return m
        return ""

    # def forward(self, m: str) -> str:
    #     return self.device.send_command(m)

    # def receive(self, m: str) -> str:
    #     return m


class Handler(Input, Output):
    # inherits methods from both input and output classes
    def __init__(self):
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

    def client_to_rpi(self, m: str | None = None) -> str: ...

    def rpi_to_host(self, m: str): ...

    def rpi_to_client(self, m: str): ...


# def rpi_to_host():
#     if wifi:
#         send_wifi()
#     elif cellular:
#         send_cell()


# def host_to_rpi():
#     if wifi:
#         listen_wifi()
#     elif cellular:
#         listen_cell()


# def rpi_to_client():
#     if radio:
#         send_radio()
#     else:
#         send_direct()


# def client_to_rpi():
#     if radio:
#         listen_radio()
#     else:
#         listen_direct()

# def send_wifi():
