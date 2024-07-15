# * * * * * ~/MotheterRemote/scripts/runradio.sh
if [ $(ps -ef | grep [l]ora_child) = "" ] ; then
    /usr/bin/python3 ~/MotheterRemote/comms/lora_child.py > tmp/lora_child.log 2>&1
fi
