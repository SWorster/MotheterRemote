#!/bin/bash

processes=$(ps -ef | grep [r]pi_wifi)
if [[ $? == 1 ]]; then # grep found nothing
    echo "Not running rpi_wifi! Running..."
    nohup /usr/bin/python3 ~/MotheterRemote/comms/rpi_wifi.py >> /tmp/rpi_wifi 2>&1 &
    echo "Will not output again until rpi_wifi stops or an error occurs."
elif [[ $processes ]]; then # grep returned something
    : # do nothing
elif [[ $? != 0 ]]; then # error
    echo "Command failed (not grep)."
else # something else went wrong
    echo "Command failed."
fi