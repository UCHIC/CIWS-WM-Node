# Instructions:</br></br>
Add this folder (Software) to the directory `/home/pi` of your Raspberry Pi 3.</br>
From the Software directory, run the following commands:
```
chmod +x setup.sh
sudo ./setup.sh
```
You can now use the Logger module in Python. Note that this was built with Python 2.7. The script will power off the Raspberry Pi, as a reboot is required for all changes to take effect.</br></br>
The following dependencies should be automagically installed by running setup.sh on the Raspberry Pi, assuming the Raspberry Pi is connected to the internet.
```
python-dev
python-smbus
wiringpi
```
The script setup.sh will run raspi-config so that the network interface may be configured if needed.

WARNING: This code is still under development and not quite ready for use</br>
