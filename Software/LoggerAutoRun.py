import Logger
import os

# The following six lines of code MUST ABSOLUTELY appear in this order. DO NOT MOVE OR CHANGE THE FOLLOWING SIX LINES OF CODE.
# Logger.initPins() Should never be called by the user. It should only be called when this script is automatically run.

Logger.init()			# Initialzie the Logger Python module.
Logger.initPins()		# Sets pins to initial state. This function should only be called once, when called automatically when powered on.
Logger.setRomBusy()		# Tell the AVR datalogger that the EEPROM chip is in use
Logger.setPowerGood()		# Tell the AVR datalogger that the Raspberry Pi is powered on
dataTuple = Logger.loadData()	# Read the data from the EEPROM chip
Logger.setRomFree()		# Tell the AVR datalogger that the EEPROM chip is no longer in use.

filename = "/home/pi/Software/data/output_" + '-'.join([str(dataTuple[2]), str(dataTuple[3]), str(dataTuple[1])]) + '_' + '-'.join([str(dataTuple[4]), str(dataTuple[5]), str(dataTuple[6])]) + ".csv"
#if os.path.isdir("/home/pi/Software/data") == False:
#	os.system("mkdir /home/pi/Software/data")
if os.path.exists(filename) == False:
	Logger.writeToFile(dataTuple, filename)

# Process the contents of dataTuple here. The format is as follows:
# Index    |    dataTuple
# ---------------------------------------------------------
#  0	         Number of Records
#  1             Year logging started
#  2             Month logging started
#  3             Day logging started
#  4             Hour logging started
#  5             Minute logging started
#  6             Second logging started
#  7             Data Byte
#  8		 Data Byte
#  9		 Data Byte
# 10		 Data Byte
# ...		 ...

if (dataTuple[0] == Logger.bufferMax()):	# This means that the Pi was turned on by the Datalogger, not a user, so it should turn itself off.
	Logger.setPowerOff()			# Tell the AVR datalogger that the Raspberry Pi is shutting down.
	os.system("sudo poweroff")		# Shut down the Raspberry Pi
