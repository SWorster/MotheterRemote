"""
Please update this file with the correct information for your setup before trying to run anything.
"""

"""Info about the host computer. This should be a computer with a static IP."""
host_data_path = "/Users/robsonlab/moths"  # where to store collected data (not in repo)
host_name = "robsonlab"  # host server's username
host_addr = "131.229.74.144"  # ip or ddns for host computer


"""Info about main RPi. Careful: this is the RPi that the server will talk to, which may or may not be the one attached to the sensor device."""
rpi_name = "pi"  # the username, not the hostname
rpi_repo = "/home/pi/MotheterRemote/comms"  # path to this repo directory
rpi_data_path = "/home/pi/mothdata"  # where sensor stores its data (NOT in repo)
rpi_addr = "10.10.32.91"  # ip or ddns address


"""main RPi's radio connection, if applicable"""
R_ADDR = "/dev/ttyUSB_LORA"  # main RPi's port to the LoRa device
R_BAUD = 115200  # baud rate


"""Info about accessory RPi, if it exists"""
acc_repo = "/home/pi1/MotheterRemote/comms"  # path to this repo directory
acc_data_path = "/home/pi1/mothdata"  # where sensor stores its data (NOT in repo)
acc_lora_port = "/dev/ttyUSB_LORA"  # accessory RPi's LoRa port


"""Sensor device information"""
observatory_name = "macleish"
device_type = "SQM-LU"  # must be SQM-LU or SQM-LE
device_addr = "/dev/ttyUSB_SQMsensor"  # port on RPi that connects to the sensor
debug = True  # whether to raise exceptions if something goes a little sideways
tries = 3  # how many reconnection attempts to make


"""Sensor connection for LU only"""
LU_BAUD = 115200  # baud rate for SQM-LU
LU_TIMEOUT = 2  # timeout for SQM-LU connections in seconds


"""Sensor connection for LE only"""
LE_PORT = 10001  # port number for SQM-LE
LE_TIMEOUT = 20  # timeout for SQM-LE connections in seconds
LE_SOCK_BUF = 256  # socket buffer size for SQM-LE connections


"""Socket info"""
host_server = 12345  # host server port
rpi_server = 54321  # rpi server port
msg_len = 1024  # length of message to send through socket


"""Text/byte formatting"""
EOL = "\n"  # end of line character (where to split array of multiple responses)
EOF = "\r"  # end of file character (marks end of a message)
utf8 = "utf-8"  # encoding method for strings<->bytes
hex = "hex"  # encoding method for SQM-LE sensor ONLY


"""Timing"""
long_s = 5  # time to wait for long tasks (eg. killing and resetting programs)
mid_s = 1  # time to wait for mid-length tasks (eg. between taking readings)
short_s = 0.1  # time to wait for short tasks (eg. between sending messages in a series)


"""Miscellaneous"""
remote_start = False  # whether to start rpi_wifi remotely
