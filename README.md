# MotheterRemote

intro text goes here

# Setup

## Set up the OS

General setup instructions can be found [here](https://www.raspberrypi.com/documentation/computers/getting-started.html), but there are a few specific steps you'll need to follow for this project.

Go to [the Raspberry Pi OS page](https://www.raspberrypi.com/software/) and download the imager that corresponds to your computer's operating system. Install the imager and try running it. Clicking on Storage should show an empty window, because we haven't given it a volume to write to yet.

Remove the SD card from your RPi and connect it to your computer via an SD card adapter. You should now see a volume to write to in the Storage window. Under Device, select the model of Raspberry Pi you're using. Under Operating System, select Raspberry Pi OS (64-bit). Click Next once you've made these selections.

Now click the Edit Settings button. Set the hostname to something unique (mine are rp1, rp2, rp3, etc.). I recommend making the username the same as the hostname, for simplicity. Set a password, and write it down somewhere. Configure the Wireless LAN (this just means WiFi) by providing the network's name and password. If you're using an institution's WiFi, you might have to select Hidden SSID (it doesn't hurt to select this by default). Select your country code in the Wireless LAN Country menu. Finally, set your time zone and keyboard layout.

In the Services menu, enable SSH with password authentication, then save your changes and click Yes twice. You may need to provide your password (for your computer, not the one you just made). After a few minutes, the install will finish and you can eject the SD card.

Connect your RPi to power using the provided power cable. Connect a mouse and keyboard with USB cables, and connect a monitor with a microHDMI cable. You should now be able to use the RPi as a computer!

## Connection Options

Your host computer needs a reliable connection to the RPi. The three options to achieve this are Ethernet, WiFi, and Cellular. For Ethernet and WiFi connections, setting up [SSH Key Sharing](#sshkey) is strongly recommended.

### Ethernet {#ethernet}

If your device will be connected to the host computer via Ethernet, follow the instructions in this section. Otherwise, continue to the [WiFi](#wifi) section below.

Plug an Ethernet cable into your device, then find the network connection icon on the taskbar (when connected to WiFi, this looks like a fan. When connected to Ethernet, it looks like two arrows). Mousing over this icon will show your IP address(es), and clicking on it will show you the available LAN networks. Select Advanced Options > Connection Information to view more information about all active connections.

Connect your computer to Ethernet. It's important to note that your computer will try to use one connection by default for everything, so you can't use Ethernet to connect to the RPi and WiFi for everything else (not easily, at least). In your computer's network settings, change the service order to put the Ethernet LAN first, ahead of any wireless options (alternatively, you can turn off WiFi just to test the Ethernet connection). Do the same on the RPi (it's easier to just disable WiFi in this case).

In a terminal, run the command `ssh rp1@rp1.local` and provide RPi's password to log in. You can now run commands on the RPi. Use Control-D to exit the RPi.

### WiFi {#wifi}

Mouse over the WiFi symbol on the RPi to view its IP. On your computer, run the command `ssh rp1@<IP>`. If you already followed the [Ethernet](#ethernet) and [SSH Key Sharing](#sshkey) directions, it should recognize that you're connecting to the same device as before and you won't have to redo that process.

### Cellular

Haven't tried this yet, will update with process.

### SSH Key Sharing {#sshkey}

If we want to use SSH for automated communication, we don't want our programs to sit around and wait for us to put the password in. We can make this automatic by creating and sharing an SSH key pair.

Your computer should already have an SSH key. You can check this by running `ls -al ~/.ssh`. If you get an error saying that `/.ssh` doesn't exist, run `ssh-keygen` to create a new ssh key.

Run the command `ls -al ~/.ssh`. There should be a file called `id_ed_25519` (it might be called something different, like DSA, RSA, or ECDSA depending on which encryption scheme was used to generate it). Copy this SSH key to the RPi with the command:
```bash
ssh-copy-id -i ~/.ssh/id_ed25519 rp1@rp1.local
```

Now try `ssh rp1@rp1.local again`; you shouldn't have to use the RPi's password to log in. You can repeat this process in reverse to make your computer accessible via the RPi, although you may have to change the remote login settings on your computer to allow incoming SSH connections.

If you get an error saying the remote host identification has changed, you need to remove any existing keys that might be associated with your RPi (this is why your computers should all be named differently: it's a pain to redo SSH keys between three computers all named "rpi"). Run the following command to remove it:
```bash
ssh-keygen -R rp1.local
```

## Connecting to the Sensor

In the RPi's start menu, go to Preferences > Raspberry Pi Configuration. In the Interfaces tab enable the serial port and serial console. In the Display tab, turn screen blanking off.

### Fixed USB port names

We need to make sure we can always connect to the sensor, even if the RPi reboots or it gets plugged into a different USB port.

#### Simplified version

Unplug and replug the sensor, then run `dmesg`. The last batch of messages should be about a FTDI USB Serial Device; record its `idVendor` and `idProduct`. Run the command `sudo nano /etc/udev/rules.d/10-usb-serial.rules`. Write the following line with the device's attributes:
```bash
SUBSYSTEM=="tty", ATTRS{idProduct}=="6001", ATTRS{idVendor}=="0403", SYMLINK+="ttyUSB_SQMsensor"
```
Save and exit, then run `sudo udevadm trigger`, and check with `ls -l /dev/ttyUSB*`.

#### Longer educational version

Open a terminal and run the command `dmesg`. It prints all diagnostic messages, which there are a ton of because things have been happening to your RPi since it booted up. To clear these messages, run `sudo dmesg -c`, which prints all the messages and then clears them. Running `dmesg` now shouldn’t print anything.

Unplug and replug your mouse, then run `dmesg` again. You should see a USB message about a disconnect, then a bunch about new device details. The orange text on the left will tell you where the diagnostic message originated: `usb 1-1.2`, for example. Find the line that contains the fields `idVendor` and `idProduct`. Write these numbers down, along with the USB number in orange.

Repeat this process for all of your USB equipment, including your sensor (but not the HDMI connection, that’s a different system!). Be on the lookout for anything with a `ttyUSB` or `ttyACM` port number, and record that if you see it. You can also run `dmesg | grep tty` to isolate just the `tty` information.

| Device      | USB port | idVendor | id Product | tty     |
| ----------- | -------- | -------- | ---------- | ------- |
| SQM sensor  | 1-1.1    | 0403     | 6001       | ttyUSB0 |
| LoRa device | 1-1.3    | 1a86     | 55d3       | ttyACM0 |
| Keyboard    | 1-1.4    | 04d9     | 0024       |         |
| Mouse       | 1-1.3    | 413c     | 301a       |         |

Note that plugging things into different USB ports can change the USB number, so don't worry if there's overlap in that column.

The `idVendor` and `idProduct` are coded into each device and can't be changed. If you have two `tty` devices with the same `idVendor` and `idProduct` values (such as two LoRa radios), you'll need to use other attributes to distinguish them. Run the command
`udevadm info --name=/dev/<tty_port> --attribute-walk` for both devices. Write down the `ID_USB_SERIAL_SHORT` value for each and use them as attributes in the next step.

Now we get to actually write our rules for the ports. Run the command:
```bash
sudo nano /etc/udev/rules.d/10-usb-serial.rules
```
Each line we write here will correspond to one device, so we only need one line for the sensor. Come up with a good name for the sensor (I’m using SQMsensor) that will differentiate it from any other devices we could attach.

```bash
SUBSYSTEM=="tty", ATTRS{idProduct}=="6001", ATTRS{idVendor}=="0403", SYMLINK+="ttyUSB_SQMsensor"
SUBSYSTEM=="tty", ATTRS{idProduct}=="55d3", ATTRS{idVendor}=="1a86", SYMLINK+="ttyUSB_LORA"
```
If you have multiple versions of the same device, you can add them as shown:

```bash
SUBSYSTEM=="tty", ATTRS{idProduct}=="55d3", ATTRS{idVendor}=="1a86", ATTRS{ID_SERIAL_SHORT}=="578E023173", SYMLINK+="ttyUSB_LORA0"
SUBSYSTEM=="tty", ATTRS{idProduct}=="55d3", ATTRS{idVendor}=="1a86", ATTRS{ID_SERIAL_SHORT}=="578E023029", SYMLINK+="ttyUSB_LORA1"
```

Save your changes and exit. Load these changes with `sudo udevadm trigger`, and check that it worked with `ls -l /dev/tty*`

If it worked, `/dev/ttyUSB_SQMsensor` will show up in light blue. If it didn’t work, go back to that file you wrote and check for typos (like `ATRS` instead of `ATTRS` or `=` instead of `==`).

## Py3SQM

The USB stick that came with the sensor has a few files you'll need. You can also access them through [this webpage](http://unihedron.com/projects/darksky/cd/index.html). Select RPi, then download Py3SQM.zip. Extract it by right-clicking and select Extract Here. You’ll get a bunch of files in a Py3SQM folder; keep this on the Desktop for easy access. It should contain a folder called pysqm containing the following: `common.py`, `__init__.py`, `__main__.py`, `main.py`, `plot.py`, `read.py`, `settings.py`. They may have been moved outside the pysqm folder when you extracted them; just remake the folder and put them back in.

Read the README.txt to get a sense of what this all does. Then start following their instructions to modify `config.py`, elaborated here:

- Observatory
    - name = MacLeish
    - latitude = 42.449183
    - longitude = 72.679909 (for testing purposes, you can put in 150 and pretend you’re in Australia, where it’s night)
    - altitude = 52 (it's in meters)
- Device
    - type = SQM_LU
    - location_name = ‘Smith College - MacLeish Field Station’
    - data_supplier = ‘Mariana Abarca / Smith College Biology Department’
    - addr =  ‘/dev/ttyUSB_SQMsensor
- Time
    - local timezone = -4 (the UTC where the sensor is located)
    - computer timezone = -4 (the UTC where the computer running this code is located)
- Directories
    - monthly data directory = “/var/tmp/sqm_macleish”
    - daily_data_directory = monthly_data_directory_+“/daily_data/”
    - daily_graph_directory = monthly_data_directory_+“/daily_graphs/”

You’ll also need to manually fix a bug. In the pysqm folder, open `plot.py`. At the top of the method `window_smooth`, write the following (be sure to only use spaces, NOT tabs):

```python
if isinstance(x,list):
	x = np.array(x)
```

Finally, run the following commands:

```bash
sudo apt install python3-ephem
sudo apt install python3-matplotlib
cd Desktop
cd Py3SQM
python -m pysqm
```

### Troubleshooting

Note that some combinations of longitude and local/computer timezone can cause unexpected behaviors. Running it during the day (or giving it a position/timezone that implies it’s day) will make it wait until night, which is useless for testing.

One possible error is `“unsupported operand type(s) for +: ‘NoneType’ and ‘datetime.timedelta’”`, which happens if the program can’t resolve when “night” should be and defaults to “None”. Try resetting to the original values long=-70, local time =-4, computer time = -4.

You might also see `“Warning, < 10 points in astronomical night, using the whole night data instead”`. This has to do with the plotting program, so you can try messing with the plotting variables in `config.py` (but we’re not worried about the graphing part of this program, just data collection, so don’t worry about this).

If you’re still getting errors about missing packages or python versions, wipe the SD card and start from the beginning. Seriously, it’s easier than messing with versions of Python and pip.

## Clone this repository

Clone this repository onto the RPi:
```bash
git clone https://github.com/SWorster/MotheterRemote
```


## Set up cronjobs

We'll need to set up new cron jobs for the Raspberry Pi (or both, if using a radio setup).

In a terminal, type `crontab -e` to add a new cron job. At the bottom of the file, insert:

```bash
* * * * * sudo chmod +x ~/MotheterRemote/scripts/runrpi.sh >> /tmp/file 2>&1

* * * * * /bin/bash ~/MotheterRemote/scripts/runrpi.sh >> /tmp/file 2>&1

0 12 * * 0 rm /tmp/file ; rm /tmp/lora_child.log
```

For the radio RPi, add the following instead:

```bash
* * * * * sudo chmod +x ~/MotheterRemote/scripts/runradio.sh >> /tmp/file 2>&1

* * * * * /bin/bash ~/MotheterRemote/scripts/runradio.sh >> /tmp/file 2>&1

0 12 * * 0 rm /tmp/file ; rm /tmp/rpi_wifi.log
```

The first line will ensure we have the authority to run the shell script, and the second actually runs it. We put the output of all of this into a file in the temporary directory, which we can use to debug in the case that something goes wrong. The third line clears out the output files every Sunday at noon so that they don't hog the memory.

After saving the files, run `sudo service cron reload` to update the changes.