# * * * * * ~/MotheterRemote/scripts/runrpi.sh
# if [ $(ps -ef | grep [r]pi_wifi) = "" ] ; then
#     /usr/bin/python3 ~/MotheterRemote/comms/rpi_wifi.py > tmp/rpi_wifi.log 2>&1
# fi

processes = $(ps -ef | grep [r]pi_wifi)
if [[ $? != 0 ]]; then
    echo "Command failed."
elif [[ $processes ]]; then
    echo "Already running rpi_wifi"
else
    echo "Not running rpi_wifi! Running..."
    /usr/bin/python3 ~/MotheterRemote/comms/rpi_wifi.py > tmp/rpi_wifi.log 2>&1
fi