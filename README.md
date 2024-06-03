# MotheterRemote
just experimenting with data transfer options for the motheter project

# primary objective
get a server at smith (or for smith) to receive and store data. get sensor at macleish to transmit its data to that server.

## secondary objectives
it would be nice to be able to tell the sensor what to do in real time. so i'm writing a python program sensor_interface.py, where we can type command-line prompts, it translates that to the corresponding command string, then transmits that to the RPi that runs the sensor. it sends the sensor's response code back to us and we get terminal output. in theory.