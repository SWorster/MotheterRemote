import socket
import configs
import rpi_to_sensor


def listener() -> None:
    # create a socket object
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_ip = configs.sensor_addr
    port = 12345

    server.bind((server_ip, port))  # bind the socket to a specific address and port
    server.listen(5)  # listen for incoming connections
    print(f"Listening on {server_ip}:{port}")

    client_socket, client_address = server.accept()  # accept incoming connections
    print(f"Accepted connection from {client_address[0]}:{client_address[1]}")

    import time

    timeout = time.time() + 60 * 5  # 5 minutes from now
    test = 0
    # receive data from the client
    while True:
        if test == 5 or time.time() > timeout:
            break
        test = test - 1

        request_bytes = client_socket.recv(1024)
        request = request_bytes.decode("utf-8")  # convert bytes to string

        if request.lower() == "close":
            client_socket.send("closed".encode("utf-8"))
            break

        print(f"Received: {request}")

        msg = rpi_to_sensor.to_sensor(request)
        if msg != "":
            response = msg.encode("utf-8")  # convert string to bytes
            client_socket.send(response)
            client_socket.send("closed".encode("utf-8"))
            break

    client_socket.close()
    print("Connection to client closed")
    server.close()


listener()
