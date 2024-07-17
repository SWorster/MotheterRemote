#!/bin/bash

processes=$(ps -ef | grep [p]ysqm)
if [[ $? == 1 ]]; then # grep found nothing
    echo "Not running pysqm module! Running..."
    nohup /usr/bin/python3 -m ~/MotheterRemote/Py3SQM/pysqm >> /tmp/sensor 2>&1 &
    echo "Will not output again until pysqm stops or an error occurs."
elif [[ $processes ]]; then # grep returned something
    : # do nothing
elif [[ $? != 0 ]]; then # error
    echo "Command failed (not grep)."
else # something else went wrong
    echo "Command failed."
fi