import Logger
import datetime
import piHandler

####
##This file is a wrapper for the logger.c module
####

##
#Handles the initialization of the serial busses and commmunication gpio
##
def initialize(firstBoot=False):
	Logger.init()  # Initialize the Logger Python module.
	if firstBoot:
		Logger.initPins()
	Logger.setPowerGood()  # Tell the AVR datalogger that the Raspberry Pi is powered on

def writeEEPROMToFile():
	Logger.setRomBusy()  # Tell the AVR datalogger that the EEPROM chip is in use
	Logger.init()
	tup = Logger.loadData()  # Read the data from the EEPROM chip
	Logger.setRomFree()  # Tell the AVR datalogger that the EEPROM chip is no longer in use.
	print(tup)
	# Write data to file
	file = "/home/pi/Software/data/site" + str(piHandler.readConfig('Site')).zfill(4) + "_20" + str(tup[1]).zfill(2) + str(tup[2]).zfill(2) + str(tup[3]).zfill(2) + 'T' + str(tup[4]).zfill(2) + str(tup[5]).zfill(2) + str(tup[6]).zfill(2) + ".csv"
	f = open(file,'w+')
	f.write('Site #: ' + str(piHandler.readConfig('Site')) + '\n')
	f.write('Datalogger ID #: ' + str(piHandler.readConfig('ID')) + '\n')
	f.write('Meter Resolution: ' + str(piHandler.readConfig('meterResolution')) + '\n')
	f.write('Time,Record,Pulses\n')
	print((tup[1], tup[2], tup[3], tup[4], tup[5], tup[6]))
	date = datetime.datetime(tup[1], tup[2], tup[3], tup[4], tup[5], tup[6])
	timerResolution = piHandler.readConfig('Period')
	for index, data in enumerate(tup[7:]):
		date = date + datetime.timedelta(0,int(timerResolution))
		f.write(date.strftime("%Y-%m-%d %H:%M:%S"))
		f.write(',')
		f.write(str(index+1))
		f.write(',')
		f.write(str(data))
		f.write('\n')
	f.close()
	return tup[0]  # returns number of records

def getArduinoReport():
	data = [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255]
	Logger.init()
	report = Logger.reportSwap(data)
	return {'year': report[0], 'month': report[1], 'day': report[2], 'hour': report[3], 'minute': report[4], 'second': report[5], 'lastPeriodPulses': report[6], 'totalPulses1': report[7], 'totalPulses2': report[8], 'totalPulses3': report[9], 'isLogging': report[10], 'period': report[11]}

def startLogging():
	data = [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 1, 255]
	Logger.init()
	Logger.reportSwap(data)

def stopLogging():
	data = [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 0, 255]
	Logger.init()
	Logger.reportSwap(data)

def setDateTime(year, month, day, hour, minute, second):
	data = [year, month, day, hour, minute, second, 255, 255, 255, 255, 255, 255]
	Logger.init()
	Logger.reportSwap(data)

def setTimerResolution(resolution):
	data = [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, resolution]
	Logger.init()
	Logger.reportSwap(data)

def bufferMax():
	return Logger.bufferMax()
