"""
Please update this file with the correct information for your setup before trying to run anything.
All code relating to SQM sensor communication was unceremoniously copied from the Py3SQM project and has been extensively modified (bastardized). If you find yourself needing to debug or rework anything in that area, I recommend checking that project for assistance. I attempted to improve upon Py3SQM but was unsuccessful. However, my experimentation did result in a moderately cleaner, semi-type-checked, and better-documented version of the project.
This code suite was only tested on an SQM-LU device. The framework for an SQM-LE exists, but you may have to debug it yourself (sorry, not much I could do on that front without the actual device). 
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
rpi_data_path = "/var/tmp/sqm_macleish/"  # path where data gets saved (NOT in repo)
rpi_image_path = "/var/tmp/images/"  # path where camera images saved (NOT in repo)
rpi_name = "rp3"
rpi_ip = "131.229.147.51"
rpi_ddns = "macleishmoths.ddns.net"  # ddns recommended if available
ddns_over_ip = True  # whether to use the ddns address or the ip
if ddns_over_ip:
    rpi_addr = rpi_ddns
else:
    rpi_addr = rpi_ip
rpi_is_wifi = True  # if the RPi uses a wifi connection
rpi_is_cellular = False  # if the RPi uses a cellular connection
rpi_is_radio = False  # if the RPi uses LoRa to talk to an accessory RPi
rpi_lora_port = ""

"""Info about accessory RPi, if it exists"""
acc_repo = "MotheterRemote/comms"  # path to this repo directory
acc_data_path = "/var/tmp/sqm_macleish/"  # path where data gets saved (NOT in repo)
acc_image_path = "/var/tmp/images/"  # path where camera images saved (NOT in repo)
acc_lora_port = ""

#! info about accessory RPi should go here, if/when we get to that point


"""Sensor device information"""
observatory_name = "macleish"
device_type = "SQM-LU"  # must be SQM-LU or SQM-LE
device_addr = "/dev/ttyUSB0"

debug = True  # whether to raise exceptions if something goes a little sideways


"""Socket info"""
so_port = 42042  # this gets overwritten in most of the code, so it's just a backup
so_msg_size = 1024  # should be power of 2
utf8 = "utf-8"  # don't change this unless you REALLY know what you're doing.


"""settings for rpi_listener.py"""
TTL = 5  # minutes to wait before quitting
TRIES = 5  # number of attempts to make
