import socket
import serial

soc_addr = "127.0.0.1"
soc_port = 12345

ser_port = "/dev/ttyUSB0"
ser_baudrate = 115200


def send_response(msg: str) -> None:
    s = socket.socket()
    s.connect((soc_addr, soc_port))
    s.send(msg.encode())
    s.close()


def greet_sensor() -> serial.Serial:
    ser = serial.Serial(
        port=ser_port,
        baudrate=ser_baudrate,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=None,
    )
    print("connected to: ", ser.portstr)
    return ser


def talk_to_sensor(ser: serial.Serial, msg: str) -> None:
    ser.timeout = 1
    ser.write(msg.encode())
    ser.flush()
    ser.readline()
    ser.timeout = None


def listen_to_sensor(ser: serial.Serial) -> None | str:
    ser.flush()
    ser.readline()


MSGLEN = 2048


class Socket:
    def __init__(self, sock: socket.socket | None = None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host: str, port: str) -> None:
        self.sock.connect((host, port))

    def send(self, msg: bytes) -> None:
        total_sent = 0
        while total_sent < MSGLEN:
            sent = self.sock.send(msg[total_sent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            total_sent = total_sent + sent

    def receive(self) -> bytes:
        chunks: list[bytes] = []
        bytes_recd = 0
        while bytes_recd < MSGLEN:
            chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
            if chunk == b"":
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b"".join(chunks)


def main():
    pass


main()
