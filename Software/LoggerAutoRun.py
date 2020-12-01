import Logger
import os
import piHandler
import arduinoHandler

arduinoHandler.writeEEPROMToFile()

data = arduinoHandler.getArduinoReport()

piHandler.writeConfig('Period', int(data[11])) # Store the period found in the returned report (allows timestamps to be calculated in Logger.writeToFile())


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

if ((data[3] == 0 and data[4] < 5) or (data[0] >= Logger.bufferMax())):	# This means that the Pi was turned on at midnight. This is likely by the microcontroller, so it should turn itself off.
	os.system("sudo poweroff")						# Shut down the Raspberry Pi
