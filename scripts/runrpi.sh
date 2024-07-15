# * * * * * ~/MotheterRemote/scripts/runrpi.sh
if [ $(ps -ef | grep [r]pi_wifi) = "" ] ; then
    /usr/bin/python3 ~/MotheterRemote/comms/rpi_wifi.py > tmp/rpi_wifi.log 2>&1
fi
