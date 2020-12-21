import os
import piHandler
import arduinoHandler
import Logger

try:
	Logger.setPowerGood()
	data = arduinoHandler.getArduinoReport()

	print(str(data))

	piHandler.writeConfig('Period', int(data['period'])) # Store the period found in the returned report (allows timestamps to be calculated in Logger.writeToFile())

	print('After Pi Handler')

	numRecords = 0

	if data['isLogging']:
		arduinoHandler.stopLogging()
		numRecords = arduinoHandler.writeEEPROMToFile(True)
		arduinoHandler.startLogging()



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

	piHandler.processData()
	print('after process')
	if ((data['hour'] == 0 and data['minute'] < 5) or (numRecords >= arduinoHandler.bufferMax())):	# This means that the Pi was turned on at midnight. This is likely by the microcontroller, so it should turn itself off.
		os.system("sudo poweroff")						# Shut down the Raspberry Pi
except Exception as e:
	print(str(e))