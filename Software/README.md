## Instructions:</br></br>
1. Connect your Raspberry Pi to the internet. 
2. Type `sudo apt-get update` into the command line and hit enter.
3. Type `sudo apt-get install git` into the command line and hit enter.
4. Type `git clone ` into the command line and hit enter.
5. Then add this folder (`Software`) to the directory `/home/pi` of your Raspberry Pi 3.</br>
From the `Software` directory, run the following commands:
```
chmod +x setup.sh
sudo ./setup.sh
```
You can now use the `Logger` module in Python. Note that this was built with Python 3.7.</br></br>
The following dependencies should be automatically installed by running `setup.sh` on the Raspberry Pi, assuming the Raspberry Pi is connected to the internet.
```
python3-dev
python3-smbus
wiringpi
python3-requests
python3-pandas
python3-seaborn
pyhton3-sklearn
```
## Overview:</br></br>
Most of the Software functionality of the WM-Node device is described in the file `logger.c`. The C code is compiled as a Python module by the script `setup.sh`, and is used in the Python scripts in this directory.

### Files:
- `LoggerAutoRun.py`: Runs on every power up.
- `LoggerShell_CLI.py`: User interfaces for the datalogger.
- `piHandler.py`: Handles the functions primarily used by the pi.
- `arduinoHandler.py`: Handles functions used to commmunicate with arduino.
- `README.md`: This file.
- `bashrc`: Configuration file for the Raspberry Pi.
- `cmdline.txt`: Configuration file for the Raspberry Pi.
- `config.txt`: Configuration file for the Raspberry Pi.
- `logger.c`: Defines all of the functions use in the `Logger*` python scripts.
- `rc.local`: Configuration file for the Raspberry Pi.
- `setup.py`: Builds Python module Logger from `logger.c`.
- `setup.sh`: Sets up Raspberry Pi device using the files in this directory.
- `uuidcopy.c`: Copies the value for the field `root=PARTUUID=` from the original `cmdline.txt` and stores it in the new `cmdline.txt`.

WARNING: This code is still under development and not quite ready for use</br>
