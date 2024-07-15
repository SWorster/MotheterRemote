# * * * * * ~/MotheterRemote/scripts/runrpi.sh
# if [ $(ps -ef | grep [r]pi_wifi) = "" ] ; then
#     /usr/bin/python3 ~/MotheterRemote/comms/rpi_wifi.py > /tmp/rpi_wifi.log 2>&1
# fi

processes=$(ps -ef | grep [r]pi_wifi)
if [[ $? == 1 ]]; then # grep found nothing
    echo "Not running rpi_wifi! Running..."
    /usr/bin/python3 ~/MotheterRemote/comms/rpi_wifi.py > /tmp/rpi_wifi.log 2>&1 &
elif [[ $processes ]]; then # grep returned something
    echo "Already running rpi_wifi"
elif [[ $? != 0 ]]; then # error
    echo "Command failed."
else
    echo "Command failed."
fi


# if [[ $? != 0 ]]; then
#     echo "Command failed."
# elif [[ $processes ]]; then
#     echo "Already running rpi_wifi"
# else
#     echo "Not running rpi_wifi! Running..."
#     /usr/bin/python3 ~/MotheterRemote/comms/rpi_wifi.py > /tmp/rpi_wifi.log 2>&1
# fi