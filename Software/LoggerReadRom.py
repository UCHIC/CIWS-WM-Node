import Logger
import os

Logger.init()                   # Initialzie the Logger Python module.
Logger.setRomBusy()             # Tell the AVR datalogger that the EEPROM chip is in use
Logger.setPowerGood()           # Tell the AVR datalogger that the Raspberry Pi is powered on
dataTuple = Logger.loadData()   # Read the data from the EEPROM chip
Logger.setRomFree()             # Tell the AVR datalogger that the EEPROM chip is no longer in use.

# Write data to file

filename= "/home/pi/Software/data/site" + Logger.getSiteNumber().zfill(4) + "_20" + '-'.join([str(dataTuple[1]).zfill(2), str(dataTuple[2]).zfill(2), str(dataTuple[3]).zfill(2)])\
	+ 'T' + str(dataTuple[4]).zfill(2) + str(dataTuple[5]).zfill(2) + str(dataTuple[6]).zfill(2) + ".csv"

try:
	if os.path.exists(filename) == False:
        	Logger.writeToFile(dataTuple, filename)
except:
	Logger.writeToFile(dataTuple, filename)

# CALL DISAGGREGATION CODE HERE
# CALL HTTPS POST REQUEST CODE HERE
