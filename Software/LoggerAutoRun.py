import Logger
import os
import SendData

# The following six lines of code MUST ABSOLUTELY appear in this order. DO NOT MOVE OR CHANGE THE FOLLOWING SIX LINES OF CODE.
# Logger.initPins() Should never be called by the user. It should only be called when this script is automatically run.

Logger.init()			# Initialzie the Logger Python module.
Logger.initPins()		# Sets pins to initial state. This function should only be called once, when called automatically when powered on.
Logger.setRomBusy()		# Tell the AVR datalogger that the EEPROM chip is in use
Logger.setPowerGood()		# Tell the AVR datalogger that the Raspberry Pi is powered on
dataTuple = Logger.loadData()	# Read the data from the EEPROM chip
Logger.setRomFree()		# Tell the AVR datalogger that the EEPROM chip is no longer in use.

report = [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255] # Gather report data to retrieve activation time
returnReport = Logger.reportSwap(report)

Logger.storePeriod(int(returnReport[11])) # Store the period found in the returned report (allows timestamps to be calculated in Logger.writeToFile())

# Write data to file

filename= "/home/pi/Software/data/site" + Logger.getSiteNumber().zfill(4) + "_20" + '-'.join([str(dataTuple[1]).zfill(2), str(dataTuple[2]).zfill(2), str(dataTuple[3]).zfill(2)])\
	+ 'T' + str(dataTuple[4]).zfill(2) + str(dataTuple[5]).zfill(2) + str(dataTuple[6]).zfill(2) + ".csv"

try:
	if os.path.exists(filename) == False:
		Logger.writeToFile(dataTuple, filename)
except:
	Logger.writeToFile(dataTuple, filename)

# Determine what data to transmit

try:
	transmission = Logger.getTransmission()
except:
	transmission = '3' # If reading the settings file fails, default to transmitting both raw and disaggregated data
try:
	storage = Logger.getStorage()
except:
	storage = '3' # If reading the setting file fails, default to storing both raw and disaggregated data

# Process the contents of dataTuple here. The format is as follows:
# Index		 dataTuple
# ---------------------------------------------------------
#  0		 Number of Records
#  1		 Year logging started
#  2		 Month logging started
#  3		 Day logging started
#  4		 Hour logging started
#  5		 Minute logging started
#  6		 Second logging started
#  7		 Data Byte
#  8		 Data Byte
#  9		 Data Byte
# 10		 Data Byte
# ...		 ...

SendData.processData(transmission, storage)

# CALL DISAGGREGATION CODE HERE

# CALL HTTPS POST REQUEST CODE HERE
# if transmission == '1':
	# Transmit raw data file
# elif transmission == '2':
	# Transmit disaggregated data file
# elif transmission == '3':
	# Transmit both data files

if ((returnReport[3] == 0) or (dataTuple[0] >= Logger.bufferMax())):	# This means that the Pi was turned on at midnight. This is likely by the microcontroller, so it should turn itself off.
	os.system("sudo poweroff")						# Shut down the Raspberry Pi
