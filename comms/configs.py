"""
Please update this file with the correct information for your setup before trying to run anything.

There are two options for the main communication method, WiFi and cellular. Additionally, the sensor can either be connected directly to the main RPi or to an accessory RPi that uses LoRa radio to communicate with the main RPi.

Relevant files:
-configs: all values that the user might want to change. Accessed by all other files.
-ui_commands: runs on host computer. Terminal-based user interface to generate and send commands.
-parse_response: runs on host computer. Formats responses from sensor and prints to terminal.
-host_to_client: runs on the host computer (a server at your institution). Handles user input, outgoing communication, and basic data storage.
-rpi_handler: runs on the main RPi and manages inbound and outbound communications. Relies on four files for each of the communication options.
-rpi_wifi: called by rpi_handler. Uses socket to maintain a connection to the host computer.
-lora_parent: called by rpi_handler. Uses serial to communicate with accessory RPi via LoRa radio.
-lora_client: runs on accessory RPi, if it exists. Uses serial to communicate with main RPi via LoRa radio.
-sensor: runs on main RPI, or accessory RPi if using a LoRa setup. Uses serial to communicate with the SQM sensor.

All code relating to SQM sensor communication was unceremoniously copied from the Py3SQM project and has been extensively modified (bastardized). If you find yourself needing to debug or rework anything in that area, I recommend checking that project for assistance. I attempted to improve upon Py3SQM, but was unsuccessful because of the ephem module (it's coded in python 2, there's no type checking, and there is NO documentation). However, my experimentation did result in a moderately cleaner, semi-type-checked, and better-documented version of the project.

This code suite was only tested on an SQM-LU device. The framework for an SQM-LE exists, but you may have to debug it yourself (sorry, not much I could do on that front without the actual device).

To prevent your host/RPi IP address from changing, you can either request a static IP through your institution or get a DDNS address (NoIP is a good option, although you have to update and renew it monthly).
"""

"""Info about the host computer. This should be a computer with a static IP."""
host_data_path = "data"  # path within repo
host_name = "skyeworster"
host_addr = "131.229.152.158"  # ip or ddns, either should work #TODO should test this


"""Info about RPi. Careful: this is the RPi that the server will talk to, which may or may not be the one attached to the sensor device.
Using DDNS is strongly recommended, as the RPi's IP may change unpredictably. This code will use whichever address you prioritize, but you should store both of them here anyways as a backup.
#? find a way to auto-update the most recent IP for the RPi and store it here?
"""
rpi_repo = "MotheterRemote/comms"  # path to this repo directory
rpi_data_path = "/var/tmp/sqm_macleish/"  # where sensor stores its data (NOT in repo)
rpi_image_path = "/var/tmp/images/"  # where sensor stores its images (NOT in repo)

rpi_is_ethernet = False
rpi_name = "rp3"
rpi_hostname = "rp3"

rpi_is_wifi = True  # if the RPi uses a wifi connection
rpi_ip = "131.229.147.51"
rpi_ddns = "macleishmoths.ddns.net"  # ddns recommended if available
ddns_over_ip = True  # whether to use the ddns address or the ip
if ddns_over_ip:
    rpi_addr = rpi_ddns
else:
    rpi_addr = rpi_ip

rpi_is_cellular = False  # if the RPi uses a cellular connection

rpi_is_radio = True  # if the RPi uses LoRa to talk to an accessory RPi
rpi_lora_port = "/dev/tty.usbmodem578E0230291"  # main RPi's port to the LoRa device

"""Info about accessory RPi, if it exists"""
acc_repo = "MotheterRemote/comms"  # path to this repo directory
acc_data_path = "/var/tmp/sqm_macleish/"  # where sensor stores its data (NOT in repo)
acc_image_path = "/var/tmp/images/"  # where sensor stores its images (NOT in repo)
acc_lora_port = "/dev/ttyUSB_LORA"  # accessory RPI's LoRa port
BAUD = 115200  # baud rate
EOL = "\n"  # end of line character
EOF = "\r"  # end of file character (marks end of a message)

"""Sensor device information"""
observatory_name = "macleish"
device_type = "SQM-LU"  # must be SQM-LU or SQM-LE
device_addr = "/dev/ttyUSB0"  # port on RPi that connects to the sensor
debug = True  # whether to raise exceptions if something goes a little sideways
LU_BAUD = 115200  # baud rate, for SQM-LU
LE_PORT = 10001  # port number, for SQM-LE
SOCK_BUF = 256  # socket buffer size

"""Socket info"""
so_port = 42069  # this gets overwritten in most of the code, so it's just a backup
so_msg_size = 1024  # should be power of 2
utf8 = "utf-8"  # encoding method. don't change this unless you REALLY know what you're doing.

"""settings for rpi_listener.py"""
TTL = 5  # minutes to wait before quitting
TRIES = 5  # number of attempts to make
