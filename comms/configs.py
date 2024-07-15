"""
Please update this file with the correct information for your setup before trying to run anything.

There are two options for the main communication method, WiFi and cellular. Additionally, the sensor can either be connected directly to the main RPi or to an accessory RPi that uses LoRa radio to communicate with the main RPi.

Relevant files:
-configs: all values that the user might want to change. Accessed by all other files.
-ui_commands: runs on host computer. Terminal-based user interface to generate and send commands.
-parse_response: runs on host computer. Formats responses from sensor and prints to terminal.
-host_to_client: runs on the host computer (a server at your institution). Handles user input, outgoing communication, and basic data storage.
-rpi_wifi: runs on main rpi. Uses socket to maintain a connection to the host computer.
-lora_parent: called by rpi_handler. Uses serial to communicate with accessory RPi via LoRa radio.
-lora_client: runs on accessory RPi, if it exists. Uses serial to communicate with main RPi via LoRa radio.
-sensor: runs on main RPI, or accessory RPi if using a LoRa setup. Uses serial to communicate with the SQM sensor.

All code relating to SQM sensor communication was unceremoniously copied from the Py3SQM project and has been extensively modified (bastardized). If you find yourself needing to debug or rework anything in that area, I recommend checking that project for assistance. I attempted to improve upon Py3SQM, but was unsuccessful because of the ephem module (it's coded in python 2, there's no type checking, and there is NO documentation). However, my experimentation did result in a moderately cleaner, semi-type-checked, and better-documented version of the project.

This code suite was only tested on an SQM-LU device. The framework for an SQM-LE exists, but you will have to debug it yourself (sorry, not much I could do on that front without the actual device). I recommend looking at the original PY3SQM project to see how their version works.

To prevent your host/RPi IP address from changing, you can either request a static IP through your institution or get a DDNS address (NoIP is a good option, although you have to update and renew it monthly).
"""

"""Info about the host computer. This should be a computer with a static IP."""
host_data_path = "data"  # path within repo
host_name = "skyeworster"
host_addr = "10.10.30.154"  # ip or ddns, either should work #TODO should test this


"""Info about RPi. Careful: this is the RPi that the server will talk to, which may or may not be the one attached to the sensor device.
Using DDNS is strongly recommended, as the RPi's IP may change unpredictably. This code will use whichever address you prioritize, but you should store both of them here anyways as a backup.
#? find a way to auto-update the most recent IP for the RPi and store it here?
"""
rpi_name = "rp3"  # the username, not the hostname
rpi_repo = "MotheterRemote/comms"  # path to this repo directory
rpi_data_path = "/var/tmp/sqm_macleish/"  # where sensor stores its data (NOT in repo)
rpi_image_path = "/var/tmp/images/"  # where sensor stores its images (NOT in repo)

rpi_is_ethernet = False
rpi_hostname = "rp3.local"  # only necessary if connecting via Ethernet

rpi_is_wifi = True  # if the RPi uses a wifi connection
rpi_ip = "10.10.9.11"
rpi_ddns = "macleishmoths.ddns.net"  # ddns recommended if available
rpi_addr = rpi_ip  # choose which address to use: ip or ddns

rpi_is_cellular = False  # if the RPi uses a cellular connection

rpi_is_radio = True  # if the RPi uses LoRa to talk to an accessory RPi
R_ADDR = "/dev/ttyUSB_LORA"  # main RPi's port to the LoRa device
R_BAUD = 115200  # baud rate


"""Info about accessory RPi, if it exists"""
acc_repo = "MotheterRemote/comms"  # path to this repo directory
acc_data_path = "/var/tmp/sqm_macleish/"  # where sensor stores its data (NOT in repo)
# ? is this needed
acc_image_path = "/var/tmp/images/"  # where sensor stores its images (NOT in repo)
acc_lora_port = "/dev/ttyUSB_LORA"  # accessory RPI's LoRa port


"""Sensor device information"""
observatory_name = "macleish"
device_type = "SQM-LU"  # must be SQM-LU or SQM-LE
device_addr = "/dev/ttyUSB_SQMsensor"  # port on RPi that connects to the sensor
debug = True  # whether to raise exceptions if something goes a little sideways

LU_BAUD = 115200  # baud rate for SQM-LU
LU_TIMEOUT = 2  # timeout for SQM-LU connections in seconds
LE_PORT = 10001  # port number for SQM-LE
LE_TIMEOUT = 20  # timeout for SQM-LE connections in seconds
LE_SOCK_BUF = 256  # socket buffer size for SQM-LE connections

"""Socket info"""
host_server = 44444  # host server port
rpi_server = 33333  # rpi server port

EOL = "\n"  # end of line character (where to split array of multiple responses)
EOF = "\r"  # end of file character (marks end of a message)
utf8 = "utf-8"  # encoding method. don't change this unless you REALLY know what you're doing.
hex = "hex"  # encoding method for SQM-LE sensor ONLY. don't change this unless the encoding paradigm completely changes (in which case this code probably won't work anyways)


long_s = 5  # time to wait for long tasks (eg. killing and resetting programs)
mid_s = 1  # time to wait for mid-length tasks (eg. between taking readings)
short_s = 0.1  # time to wait for short tasks (eg. between sending messages in a series)

msg_len = 1024

tries = 3
