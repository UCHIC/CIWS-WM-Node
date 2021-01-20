#!/bin/bash

############################################################################################################################################
################################################################# setup.sh #################################################################
############################################################################################################################################
#                                                                                                                                          #
# This bash script builds and installs the Logger module for python 3.7.                                                                   #
# The actions taken by this script are separated into five steps:                                                                          #
#                                                                                                                                          #
#   1)  Install libraries                                                                                                                  #
#   2)  Replace files                                                                                                                      #
#   3)  Compile code                                                                                                                       #
#   4)  Reboot                                                                                                                             #
#                                                                                                                                          #
# Each step is documented further with important notes describing what the script is doing and why.                                        #
#                                                                                                                                          #
# The following changes are applied to configuration files (<> Denotes text actually added or removed):                                    #
#   1)  Add <enable_uart=1> to /boot/config.txt                                                                                            #
#   2)  Add <core_freq=250> to /boot/config.txt (The UART baudrate is dependent on the GPU core frequency, so it must be made constant)    #
#   3)  Add <dtparam=i2c_arm=on> to /boot/config.txt                                                                                       #
#   4)  Add <dtparam=spi=on> to /boot/config.txt                                                                                           #
#   5)  Add <sudo systemctl stop serial-getty@ttyS0.service> to /etc/rc.local                                                              #
#   6)  Add <sudo systemctl disable serial-getty@ttyS0.service> to /etc/rc.local                                                           #
#   7)  Add <sudo systemctl stop systemd-timesyncd> to /etc/rc.local                                                                       #
#   8)  Add <sudo systemctl disable systemd-timesyncd> to /etc/rc.local                                                                    #
#   9)  Remove <console=serial0,115200> from /boot/cmdline.txt                                                                             #
#  10)  Add <spidev.bufsiz=65536> to /boot/cmdline.txt                                                                                     #
#                                                                                                                                          #
############################################################################################################################################

#################################################################
###################### 2) Install libraries #####################
#################################################################

# NOTES:

## These are development packages used in the software on this ##
## Raspberry Pi. The package python-dev is used to build the   ##
## Logger python module, while wiringpi provides an interface  ##
## to the GPIO pins on the Raspberry Pi for the C programming  ##
## language.                                                   ##

echo "Installing python3-dev python3-smbus wiringpi python3-requests python3-pandas python3-seaborn python3-sklearn..."

apt-get update
apt-get install python3-dev python3-smbus wiringpi python3-requests python3-pandas python3-seaborn python3-sklearn

#################################################################
####################### 3) Replace files ########################
#################################################################

# NOTES:

## If the .original configuration files exist, that means they ##
## were already saved, and should not be overwritten. If they  ##
## do not exist, the current configuration files will be       ##
## appended with .original. The custom configuration files     ##
## from the repository will be copied to their respective      ##
## locations, thus changing the start-up configuration of the  ##
## Raspberry Pi. The C program uuidcopy looks up the correct   ##
## value for the field "root=PARTUUID=" for cmdline.txt, as    ##
## this value may change across different installations.       ##

echo "Configuring the Raspberry Pi..."

if [[ ! -f "/boot/cmdline.txt.original" ]]
then
	mv /boot/cmdline.txt /boot/cmdline.txt.original
fi

if [[ ! -f "/boot/config.txt.original" ]]
then
	mv /boot/config.txt /boot/config.txt.original
fi

if [[ ! -f "/etc/rc.local.original" ]]
then
	mv /etc/rc.local /etc/rc.local.original
fi

if [[ ! -f "/home/pi/.bashrc.original" ]]
then
	mv /home/pi/.bashrc /home/pi/.bashrc.original
fi

cp cmdline.txt /boot
cp config.txt /boot
cp rc.local /etc
cp bashrc /home/pi/.bashrc

gcc uuidcopy.c -o uuidcopy
./uuidcopy
rm -f uuidcopy

#################################################################
######################## 4) Compile code ########################
#################################################################

## NOTES:

## This section compiles logger.c and builds a python module   ##
## called Logger. Logger is usable in any python script on the ##
## Raspberry Pi by calling <import Logger> in the script.      ##

echo "Building Logger python module..."

rm -f -r build
rm -f /usr/local/lib/python3.7/dist-packages/Logger*
python3 setup.py build
python3 setup.py install

if [ ! -d "/home/pi/Software/data" ]
then
	echo "Creating directory for data files"
	mkdir /home/pi/Software/data
else
	echo "Directory for data files found"
fi

if [ ! -d "/home/pi/Software/savedData" ]
then
	echo "Creating directory for saved data files"
	mkdir /home/pi/Software/savedData
else
	echo "Directory for saved data files found"
fi

#################################################################
########################### 5) Reboot ###########################
#################################################################

## NOTES:

## The reboot is required mainly because of the configuration  ##
## files, which are read when the Raspberry Pi boots. Instead  ##
## of calling reboot, however, a poweroff command is executed  ##
## instead. This is because when the Raspberry Pi powers off,  ##
## the microcontroller cuts power to the Raspberry Pi without  ##
## checking to see if the Raspberry Pi is powering on again.   ##
## This introduces a condition in which the Raspberry Pi may   ##
## lose power while booting. Therefore, it is up to the user   ##
## to power the system back on again after running this        ##
## script.                                                     ##

echo " "
echo "Setup finished. A restart is required for changes to take effect."
echo " "
read -p "Press Enter to power off the Raspberry Pi."

poweroff
