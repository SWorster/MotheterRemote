#!/bin/bash
processes=$(ps -ef | grep [r]pi_wifi)
if [[ $? == 1 ]]; then # grep found nothing
    echo "Not running rpi_wifi! Running..."
    nohup /usr/bin/python3 ~/MotheterRemote/comms/rpi_wifi.py >> /tmp/rpi_wifi.log 2>&1 &
elif [[ $processes ]]; then # grep returned something
    echo "Already running rpi_wifi"
elif [[ $? != 0 ]]; then # error
    echo "Command failed (not grep)."
else # something else went wrong
    echo "Command failed."
fi