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
	Logger.init()	#Initializes the spi and uart busses
	if firstBoot:	#Checks if first boot
		Logger.initPins()	#initializes gpio communication pins(24 and 25)
	Logger.setPowerGood()	#Tell the AVR datalogger that the Raspberry Pi is powered on
	
##
#Takes data from EEPROM and formats it into a csv in the data directory
##
def writeEEPROMToFile():
	Logger.setRomBusy()  	#Tell the AVR datalogger that the EEPROM chip is in use
	Logger.init()		#Initialize the spi and uart data busses
	tup = Logger.loadData()	#Read the data from the EEPROM chip
	Logger.setRomFree()  	#Tell the AVR datalogger that the EEPROM chip is no longer in use.
	file = "/home/pi/Software/data/site" +
		str(piHandler.readConfig('Site')).zfill(4) + "_20" + 
		str(tup[1]).zfill(2) + 
		str(tup[2]).zfill(2) + 
		str(tup[3]).zfill(2) + 'T' + 
		str(tup[4]).zfill(2) + 
		str(tup[5]).zfill(2) + 
		str(tup[6]).zfill(2) + ".csv"	#Create file name for new data
	f = open(file,'w+')			#Open file in write mode
	f.write('Site #: ' + str(piHandler.readConfig('Site')) + '\n')	#Write the site number to the file
	f.write('Datalogger ID #: ' + str(piHandler.readConfig('ID')) + '\n')	#Write the datalogging id to the file
	f.write('Meter Resolution: ' + str(piHandler.readConfig('meterResolution')) + '\n')	#Write meter resolution to file. 
	f.write('Time,Record,Pulses\n')		#Write headers for columns
	date = datetime.datetime(tup[1], tup[2], tup[3], tup[4], tup[5], tup[6])	#Convert date into datetime object
	timerResolution = piHandler.readConfig('Period')				#Get timer resolution value
	for index, data in enumerate(tup[7:]):						#For every data point
		date = date + datetime.timedelta(0,int(timerResolution))		#Create date object
		f.write(date.strftime("%Y-%m-%d %H:%M:%S"))				#Write date object to file
		f.write(',')								#Write , to file
		f.write(str(index+1))							#Write index of data to file
		f.write(',')								#Write , to file
		f.write(str(data))							#Write data to file
		f.write('\n')								#Write return char to file
	f.close()									#Close file
	return tup[0]  # returns number of records

##
#Returns information the microcontroller uses to operate
##
def getArduinoReport():
	data = [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255]	#All 255 so no changes made
	Logger.init()									#Initialize serial buses
	report = Logger.reportSwap(data)						#Swap data with microcontroller
	return {'year': report[0], 'month': report[1], 'day': report[2], 'hour': report[3], 'minute': report[4], 'second': report[5], 'lastPeriodPulses': report[6], 'totalPulses1': report[7], 'totalPulses2': report[8], 'totalPulses3': report[9], 'isLogging': report[10], 'period': report[11]}

##
#Send a command to the microcontroller that initiates logging
##
def startLogging():
	data = [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 1, 255]	#Create data array with logging parameter set to 1
	Logger.init()								#Initialize serial buses
	Logger.reportSwap(data)							#Swap data with microcontroller

##
#Send command to the microcontroller that stops logging
##
def stopLogging():
	data = [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 0, 255]	#Create data array with logging parameter set to 0
	Logger.init()								#Initialize serial buses
	Logger.reportSwap(data)							#Swap data with microcontroller

##
#Set the date and time on the RTC
##
def setDateTime(year, month, day, hour, minute, second):
	data = [year, month, day, hour, minute, second, 255, 255, 255, 255, 255, 255]	#Create data array with date and time fields set
	Logger.init()								#Initialize serial buses
	Logger.reportSwap(data)							#Swap data with microcontroller

##
#Send command to change the timer resolution
##
def setTimerResolution(resolution):
	data = [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, resolution]	#Create data array with timer resolution field set
	Logger.init()								#Initialize serial buses
	Logger.reportSwap(data)							#Swap data with microcontroller

##
#Returns the max buffer length
##
def bufferMax():
	return Logger.bufferMax()
