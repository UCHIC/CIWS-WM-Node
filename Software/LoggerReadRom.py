import Logger
import os
import SendData

Logger.init()                   # Initialzie the Logger Python module.
Logger.setRomBusy()             # Tell the AVR datalogger that the EEPROM chip is in use
Logger.setPowerGood()           # Tell the AVR datalogger that the Raspberry Pi is powered on
print("PowerGoodReadRom")
dataTuple = Logger.loadData()   # Read the data from the EEPROM chip
Logger.setRomFree()             # Tell the AVR datalogger that the EEPROM chip is no longer in use.

# Write data to file
filename= "/home/pi/Software3/data/site" + Logger.getSiteNumber().zfill(4) + "_20" + '-'.join([str(dataTuple[1]).zfill(2), str(dataTuple[2]).zfill(2), str(dataTuple[3]).zfill(2)])\
	+ 'T' + str(dataTuple[4]).zfill(2) + str(dataTuple[5]).zfill(2) + str(dataTuple[6]).zfill(2) + ".csv"

try:
	if os.path.exists(filename) == False:
		pass #Logger.writeToFile(dataTuple, filename)
except:
	pass #Logger.writeToFile(dataTuple, filename)

# Determine what data to transmit

try:
	transmission = Logger.getTransmission()
except:
	transmission = '3' # If reading the settings file fails, default to transmitting both raw and disaggregated data
try:
	storage = Logger.getStorage()
except:
	storage = '3'  # If reading the setting file fails, default to storing both raw and disaggregated data

SendData.processData(transmission, storage)

# CALL DISAGGREGATION CODE HERE

# CALL HTTPS POST REQUEST CODE HERE
# if transmission == '1':
        # Transmit raw data file
# elif transmission == '2':
        # Transmit disaggregated data file
# elif transmission == '3':
        # Transmit both data files

