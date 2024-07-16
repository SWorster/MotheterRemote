#!/bin/bash
processes=$(ps -ef | grep [l]ora_child)
if [[ $? == 1 ]]; then # grep found nothing
    echo "Not running lora_child! Running..."
    nohup /usr/bin/python3 ~/MotheterRemote/comms/lora_child.py >> /tmp/lora_child.log 2>&1 &
elif [[ $processes ]]; then # grep returned something
    echo "Already running lora_child"
elif [[ $? != 0 ]]; then # error
    echo "Command failed (not grep)."
else # something else went wrong
    echo "Command failed."
fi
