import socket

s = socket.socket()
port = 12345
s.connect(("131.229.147.51", port))
s.send("this is a test\n".encode())
print(s.recv(1024).decode())
s.close()
