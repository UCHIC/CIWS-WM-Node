import Logger
import datetime
def writeToFile(tup, file):
	f = open(file,'w+')
	f.write('Site #: '+str(Logger.getSiteNumber())+'\n')
	f.write('Datalogger ID #: '+str(Logger.getID())+'\n')
	f.write('Meter Resolution: '+str(Logger.getMeterResolution())+'\n')
	f.write('Time,Record,Pulses\n')
	date = datetime.datetime(tup[1],tup[2],tup[3],tup[4],tup[5],tup[6])
	timerResolution = Logger.getPeriod()
	for index, data in enumerate(tup[7:]):
		date = date + datetime.timedelta(0,int(timerResolution))
		f.write(date.strftime("%y-%m-%d %H:%M:%S"))
		f.write(',')
		f.write(str(index+1))
		f.write(',')
		f.write(str(data))
		f.write('\n')
