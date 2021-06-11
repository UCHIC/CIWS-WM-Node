import os
import piHandler
import arduinoHandler

###
##This file is run everytime the pi is turned on. Its called from rc.local at start up
###

try:
	arduinoHandler.initialize(True)				#Initialize serial busses and communication GPIO
	data = arduinoHandler.getArduinoReport()		#Read report from microcontroller

	piHandler.writeConfig('Period', int(data['period']))	#Store the period found in the returned report (allows timestamps to be calculated in Logger.writeToFile())

	numRecords = 0						#Create variable numRecords

	if data['isLogging']:					#If device is logging
		numRecords = arduinoHandler.writeEEPROMToFile()	#Read data from EEPROM and format data into csv in data directory. Update numRecords


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

	piHandler.processData()					#Process files in the data directory

	if ((data['hour'] == 0 and data['minute'] < 2) or (numRecords >= arduinoHandler.bufferMax())):	# This means that the Pi was turned on at midnight. This is likely by the microcontroller, so it should turn itself off.
		os.system("sudo poweroff")						# Shut down the Raspberry Pi
except Exception as e:
	print(str(e))
