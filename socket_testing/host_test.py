import socket
import get_command
import parse_response

port = 12345


s = socket.socket()
print("Socket successfully created")
s.connect(("131.229.152.158", port))
# put the socket into listening mode
while True:
    c, addr = s.accept()
    print("Got connection from", addr)
    msg = get_command.command_from_host()
    c.send(msg.encode())
    resp = c.recv(1024)
    get_command.from_socket(resp.decode())
    parse_response.sort_response(resp.decode())
    c.close()
