#!/bin/bash

processes=$(ps -ef | grep [l]ora_child)
if [[ $? == 1 ]]; then # grep found nothing
    echo "Not running lora_child! Running..."
    nohup /usr/bin/python3 ~/MotheterRemote/comms/lora_child.py >> /tmp/lora_child 2>&1 &
    echo "Will not output again until lora_child stops or an error occurs."
elif [[ $processes ]]; then # grep returned something
    : # do nothing
elif [[ $? != 0 ]]; then # error
    echo "Command failed (not grep)."
else # something else went wrong
    echo "Command failed."
fi
