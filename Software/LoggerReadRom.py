import Logger
import os

Logger.init()                   # Initialzie the Logger Python module.
Logger.setRomBusy()             # Tell the AVR datalogger that the EEPROM chip is in use
Logger.setPowerGood()           # Tell the AVR datalogger that the Raspberry Pi is powered on
dataTuple = Logger.loadData()   # Read the data from the EEPROM chip
Logger.setRomFree()             # Tell the AVR datalogger that the EEPROM chip is no longer in use.

filename = "/home/pi/Software/data/output_" + '-'.join([str(dataTuple[2]), str(dataTuple[3]), str(dataTuple[1])]) + '_' + '-'.join([str(dataTuple[4]), str(dataTuple[5]), str(dataTuple[6])]) + ".csv"
#if os.path.isdir("/home/pi/Software/data") == False:
#        os.system("mkdir /home/pi/Software/data")
if os.path.exists(filename) == False:
        Logger.writeToFile(dataTuple, filename)
