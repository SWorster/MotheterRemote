import socket

s = socket.socket()
port = 12345
s.connect(("131.229.152.158", port))
s.send("rx".encode())
print(s.recv(1024).decode())
s.close()
