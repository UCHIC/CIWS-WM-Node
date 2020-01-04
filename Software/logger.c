/************************************************************\
 * Python Module 'Logger' for the Computational Datalogger.
 *
 * The functions in this module are designed for interacting
 * with the attached AVR based datalogger.
\************************************************************/

#include <Python.h>
#include <wiringPi.h>
#include <wiringPiSPI.h>
#include <wiringSerial.h>

#define ROM_BUSY    24
#define POWER_GOOD  25
#define BUFFER_MAX  21600
#define HEADER_SIZE 9

int serialFD;

/** Initialize the Logger Module **/

static PyObject* init(PyObject* self, PyObject* args)
{
	wiringPiSetupGpio();			// Setup the wiringPi library to use Broadcom GPIO numbers.

	int spiFD = -1;
	while(spiFD < 0)
	{
		spiFD = wiringPiSPISetup(0, 2000000);		// Setup the wiringPi SPI library to use CS 0 @ 2 MHz.
	}

	serialFD = -1;
	while(serialFD < 0)
	{
		serialFD = serialOpen("/dev/ttyS0", 9600);	// Setup the wiringPi Serial library to use the mini UART @ 9600 Baud
	}

	sleep(1);				// Delay for one second

	return Py_None;
}

static PyObject* initPins(PyObject* self, PyObject* args)
{
	pinMode(ROM_BUSY, OUTPUT);		// ROM_BUSY Pin output low
	digitalWrite(ROM_BUSY, LOW);

	pinMode(POWER_GOOD, OUTPUT);		// POWER_GOOD Pin output low
	digitalWrite(POWER_GOOD, LOW);

	sleep(1);

	return Py_None;
}

/** Return the maximum allowable buffer value **/

static PyObject* bufferMax(PyObject* self, PyObject* args)
{
	return Py_BuildValue("i", BUFFER_MAX);
}

/** Tell the AVR datalogger that the EEPROM chip is in use **/

static PyObject* setRomBusy(PyObject* self, PyObject* args)
{
	digitalWrite(ROM_BUSY, HIGH);	// Setting this pin high tells the datalogger the chip is in use

	return Py_None;
}

/** Tell the AVR datalogger that the Pi has successfully powered up **/

static PyObject* setPowerGood(PyObject* self, PyObject* args)
{
	digitalWrite(POWER_GOOD, HIGH);	// Setting this pin high tells the datalogger the Pi is on.

	return Py_None;
}

/** Read the contents of the EEPROM chip **/

static PyObject* loadData(PyObject* self, PyObject* args)
{
	unsigned int dataSize = BUFFER_MAX + HEADER_SIZE + 4;	// How many bytes to read from the EEPROM
	unsigned char data[dataSize];				// Array will hold data from the EEPROM
	data[0] = 0x03;						// Load the array with: Read instruction
	data[1] = 0x00;						//                      Address (High): 0
	data[2] = 0x00;						//                      Address (Mid):  0
	data[3] = 0x00;						//                      Address (Low):  0

	wiringPiSPIDataRW(0, data, dataSize);			// SPI Transaction: The contents of data are overwritten by the EEPROM response

	unsigned int recordNum = (data[4] << 16) + (data[5] << 8) + data[6];	// Calculate number of records stored
	if(recordNum > BUFFER_MAX)
	{
		recordNum = BUFFER_MAX;
	}

	unsigned int lastIndex = recordNum + HEADER_SIZE + 4;	// lastIndex points to the last record stored in data[]
	if(lastIndex > dataSize)
		lastIndex = dataSize;

	PyObject* dataTuple = PyTuple_New(recordNum + 7);	// The dataTuple is what will be used in the Python script Logger is used in.

	PyObject* PyData = Py_BuildValue("i", recordNum);	// To store data in dataTuple, we need a PyObject.

	PyTuple_SetItem(dataTuple, 0, PyData);			// The first value in dataTuple is the number of records it holds.

	unsigned int i;
	for(i = 7; i <= lastIndex; i++)				// This loop fills dataTuple with date/time and records.
	{
		PyData = Py_BuildValue("b", data[i]);
		PyTuple_SetItem(dataTuple, i - 6, PyData);
	}

	return dataTuple;					// dataTuple is returned for use in a Python script
}

/** Exchange Reports with the AVR datalogger **/

static PyObject* reportSwap(PyObject* self, PyObject* args)
{
	PyObject* PyReport;

	int i;
	char report[9];

	if(!PyArg_ParseTuple(args, "O!", &PyList_Type, &PyReport))
	{
		PyErr_SetString(PyExc_TypeError, "Parameter must be a list.");
		return NULL;
	}

	for(i = 0; i < 9; i++)
	{
		report[i] = 0xFF & (char)PyInt_AS_LONG(PyList_GetItem(PyReport, i));
		serialPutchar(serialFD, report[i]);
		report[i] = (char)serialGetchar(serialFD);
		PyList_SetItem(PyReport, i, Py_BuildValue("b", report[i]));
	}

	return PyReport;
}

/** Tell the AVR datalogger that the EEPROM chip is no longer in use **/

static PyObject* setRomFree(PyObject* self, PyObject* args)
{
	digitalWrite(ROM_BUSY, LOW);

	return Py_None;
}

/** Tell the AVR datalogger that the Pi is shutting down **/

static PyObject* setPowerOff(PyObject* self, PyObject* args)
{
	digitalWrite(POWER_GOOD, LOW);
	serialClose(serialFD);

	return Py_None;
}

static PyObject* writeToFile(PyObject* self, PyObject* args)
{
	PyObject* DataList;						// DataList will hold the list of collected data.
	char* filename;							// filname will hold the name of the file to write DataList to.
	FILE* dataOut;							// Pointer to the output file.
	FILE* totalPulses;						// Pointer to the total water flow file.
	if(!PyArg_ParseTuple(args, "Os", &DataList, &filename))		// Retrieve the data and put it into DataList.
	{
		PyErr_SetString(PyExc_TypeError, "Expected a list and a string.");	// If the operation fails, set an error and return.
		return PyString_FromString("Bad arguments");
	}

	PyObject* Iterator = PyObject_GetIter(DataList);		// Create an iterator to traverse the contents of DataList
	if(!Iterator)
	{
		PyErr_SetString(PyExc_TypeError, "Error setting list iterator.");
		return PyString_FromString("Error setting list iterators.");
	}

	dataOut = fopen(filename, "w");
	if(dataOut == NULL)						// Create new data file
	{
		PyErr_SetString(PyExc_TypeError, "Could not create file.");
		return PyString_FromString("Could not create file.");
	}

	long totalPulseCount = 0;
	totalPulses = fopen("/home/pi/Software/data/totalPulseCount.dat", "r");
	if(totalPulses == NULL)
	{
		PyErr_SetString(PyExc_TypeError, "Could not open pulse count file.");
		totalPulseCount = 0;
	}
	int scan = fscanf(totalPulses, "%ld", &totalPulseCount);
	if(scan == 0)
	{
		PyErr_SetString(PyExc_TypeError, "Error reading pulse count file.");
		totalPulseCount = 0;
	}
	fclose(totalPulses);

	PyObject* next = PyIter_Next(Iterator);				// Each next holds the data from the current DataList index.

	unsigned int index = 0;
	int month = 0;
	int day = 0;
	int year = 0;
	int hour = 0;
	int minute = 0;
	int second = 0;
	const int deltaSec = 4;
	long data;
	int recordNum = 1;

	while(next != NULL)						// Print each value to the output file.
	{
		data = PyInt_AsLong(next);
		if (index < 7)
		{
		/*	if (index == 0)
				fprintf(dataOut, "Data Size: %ld\n", data);*/
			if (index == 1)
			{
				year = data;
			}
			if (index == 2)
			{
				month = data;
			}
			if (index == 3)
			{
				day = data;
			}
			if (index == 4)
			{
				hour = data;
			}
			if (index == 5)
			{
				minute = data;
			}
			if (index == 6)
			{
				fprintf(dataOut, "Time,Record,Pulses\n");
				second = data;
			}
		}
		else
		{
			fprintf(dataOut, "\"%02d-%02d-%02d %02d:%02d:%02d\",%d,%ld\n",year, month, day, hour, minute, second, recordNum, data);
			totalPulseCount += data;
			recordNum += 1;
			second += deltaSec;
			if (second >= 60)
			{
				second = second % 60;
				minute += 1;
			}
			if (minute >= 60)
			{
				minute = minute % 60;
				hour += 1;
			}
			if (hour >= 24)
			{
				hour = hour % 24;
				day += 1;
			}
			if (day >= 31)
			{
				day = 1;
				month += 1;
			}
			if (day >= 30)
			{
				if((month == 9) || (month == 4) || (month == 6) || (month == 11))	// If Month with thirty days
				{
					day = 1;
					month += 1;
				}
			}
			if (day >= 29)
			{
				if(month == 2)	// If February
				{
					day = 1;
					month += 1;
				}
			}
			if (day >= 28)
			{
				if(month ==2)	// Condition: If February and Not Leap Year
				{
					if(year % 4 == 0)
					{
						if((year % 100 != 0) || (year % 400 == 0))
						{
							day = 1;
							month += 1;
						}
					}
				}
			}
			if (month > 12)
			{
				month = 1;
				year += 1;
			}
		}
		next = PyIter_Next(Iterator);
		index += 1;
	}

	fclose(dataOut);

	totalPulses = fopen("/home/pi/Software/data/totalPulseCount.dat", "w");
	if(totalPulses == NULL)
	{
		PyErr_SetString(PyExc_TypeError, "Could not open pulse count file.");
		return PyString_FromString("Could not open pulse count file.");
	}
	fprintf(totalPulses, "%ld", totalPulseCount);
	fclose(totalPulses);

	return Py_None;
}

static PyObject* setID(PyObject* self, PyObject* args)
{
	FILE* IDconfig;
	char* newID;
	IDconfig = fopen("/home/pi/Software/config/IDconfig.txt", "w");			// Open ID Config File
	if(IDconfig == NULL)								// Check file
	{
		PyErr_SetString(PyExc_TypeError, "Could not open IDconfig.txt.");
		return PyString_FromString("Could not open IDconfig.txt.");
	}
	if(!PyArg_ParseTuple(args, "s", &newID))					// Parse arguments
        {
                PyErr_SetString(PyExc_TypeError, "Expected a string.");     	 	// If the operation fails, set an error and return.
                return PyString_FromString("Bad arguments");
        }
	fprintf(IDconfig, "%s\n", newID);						// Write new ID number
	fclose(IDconfig);

	return Py_None;									// Close ID Config File
}

static PyObject* setSiteNumber(PyObject* self, PyObject* args)
{
	FILE* siteConfig;
	char* newSite;
	siteConfig = fopen("/home/pi/Software/config/siteConfig.txt", "w");
	if(siteConfig == NULL)
	{
		PyErr_SetString(PyExc_TypeError, "Could not open siteConfig.txt.");
		return PyString_FromString("Could not open siteConfig.txt");
	}
	if(!PyArg_ParseTuple(args, "s", &newSite))
	{
		PyErr_SetString(PyExc_TypeError, "Expected a string.");                 // If the operation fails, set an error and return.
                return PyString_FromString("Bad arguments");
	}
	fprintf(siteConfig, "%s\n", newSite);
	fclose(siteConfig);

	return Py_None;
}

static PyObject* setMeterResolution(PyObject* self, PyObject* args)
{
	FILE* meterConfig;
	char* newMeterRez;
	meterConfig = fopen("/home/pi/Software/config/meterConfig.txt", "w");
	if(meterConfig == NULL)
	{
		PyErr_SetString(PyExc_TypeError, "Could not open meterConfig.txt.");
		return PyString_FromString("Could not open meterConfig.txt");
	}
	if(!PyArg_ParseTuple(args, "s", &newMeterRez))
	{
		PyErr_SetString(PyExc_TypeError, "Expected a string.");                 // If the operation fails, set an error and return.
                return PyString_FromString("Bad arguments");
	}
	fprintf(meterConfig, "%s\n", newMeterRez);
	fclose(meterConfig);

	return Py_None;
}

static PyObject* getID(PyObject* self, PyObject* args)
{
	FILE* IDconfig;
	char IDnum[] = {0, 0, 0, 0, 0};
	IDconfig = fopen("/home/pi/Software/config/IDconfig.txt", "r");
	if(IDconfig == NULL)								// Check file
	{
		PyErr_SetString(PyExc_TypeError, "Could not open IDconfig.txt.");
		return PyString_FromString("Could not open IDconfig.txt.");
	}
	int scan = fscanf(IDconfig, "%4s", IDnum);
	if(scan == 0)
	{
		PyErr_SetString(PyExc_TypeError, "Error reading IDconfig.txt.");
                return PyString_FromString("Error reading IDconfig.txt.");
	}
	fclose(IDconfig);

	return PyString_FromString(IDnum);
}

static PyObject* getSiteNumber(PyObject* self, PyObject* args)
{
	FILE* siteConfig;
	char siteNum[] = {0, 0, 0, 0, 0};
	siteConfig = fopen("/home/pi/Software/config/siteConfig.txt", "r");
	if(siteConfig == NULL)
	{
		PyErr_SetString(PyExc_TypeError, "Could not open siteConfig.txt.");
		return PyString_FromString("Could not open siteConfig.txt.");
	}
	int scan = fscanf(siteConfig, "%4s", siteNum);
	if(scan == 0)
	{
		PyErr_SetString(PyExc_TypeError, "Error reading siteConfig.txt");
		return PyString_FromString("Error reading siteConfig.txt");
	}
	fclose(siteConfig);

	return PyString_FromString(siteNum);
}

static PyObject* getMeterResolution(PyObject* self, PyObject* args)
{
	FILE* meterConfig;
	char meterRez[] = {0, 0, 0, 0, 0, 0, 0, 0, 0};
	meterConfig = fopen("/home/pi/Software/config/meterConfig.txt", "r");
	if(meterConfig == NULL)
	{
		PyErr_SetString(PyExc_TypeError, "Could not open meterConfig.txt.");
		return PyString_FromString("Could not open meterConfig.txt.");
	}
	int scan = fscanf(meterConfig, "%8s", meterRez);
	if(scan == 0)
	{
		PyErr_SetString(PyExc_TypeError, "Error reading meterConfig.txt");
		return PyString_FromString("Error reading meterConfig.txt");
	}
	fclose(meterConfig);

	return PyString_FromString(meterRez);
}

static PyObject* getTotalFlow(PyObject* self, PyObject* args)
{
	FILE* totalPulses;
	long totalPulseCount = 0;
	totalPulses = fopen("/home/pi/Software/data/totalPulseCount.dat", "r");
	if(totalPulses == NULL)
	{
		PyErr_SetString(PyExc_TypeError, "Could not open pulse count file.");
		totalPulseCount = 0;
	}
	int scan = fscanf(totalPulses, "%ld", &totalPulseCount);
	if(scan == 0)
	{
		PyErr_SetString(PyExc_TypeError, "Error reading pulse count file.");
		totalPulseCount = 0;
	}
	fclose(totalPulses);

	return PyLong_FromLong(totalPulseCount);
}

static PyObject* resetTotalFlow(PyObject* self, PyObject* args)
{
	FILE* totalPulses;
	long totalPulseCount = 0;
	totalPulses = fopen("/home/pi/Software/data/totalPulseCount.dat", "w");
	if(totalPulses == NULL)
	{
		PyErr_SetString(PyExc_TypeError, "Could not open pulse count file.");
		return PyString_FromString("Could not open pulse count file.");
	}
	fprintf(totalPulses, "%ld", totalPulseCount);

	fclose(totalPulses);

	return Py_None;
}

static PyMethodDef methods[] = {
	{ "init", init, METH_NOARGS, "Performs necessary setup to communicate with GPIO and SPI." },
	{ "initPins", initPins, METH_NOARGS, "Sets powerGood and romBusy lines low" },
	{ "bufferMax", bufferMax, METH_NOARGS, "Returns the maximum buffer size from the datalogger" },
        { "setRomBusy", setRomBusy, METH_NOARGS, "Sends a signal to the datalogger that the EEPROM chip is in use" },
        { "setPowerGood", setPowerGood, METH_NOARGS, "Sends a signal to the datalogger that the Pi booted succesfully" },
        { "loadData", loadData, METH_NOARGS, "Reads data from the EEPROM chip and returns a tuple" },
	{ "reportSwap", reportSwap, METH_VARARGS, "Swaps reports with the AVR datalogger" },
        { "setRomFree", setRomFree, METH_NOARGS, "Sends a signal to the datalogger that the EEPROM chip is not in use" },
        { "setPowerOff", setPowerOff, METH_NOARGS, "Sends a signal to the datalogger that the Pi is shutting down" },
	{ "writeToFile", writeToFile, METH_VARARGS, "Writes a list of data to a file" },
	{ "setID", setID, METH_VARARGS, "Sets a datalogger ID number" },
	{ "setSiteNumber", setSiteNumber, METH_VARARGS, "Sets a datalogger site number" },
	{ "getID", getID, METH_NOARGS, "Returns a datalogger ID number" },
	{ "getSiteNumber", getSiteNumber, METH_NOARGS, "Returns a datalogger site number" },
	{ "setMeterResolution", setMeterResolution, METH_VARARGS, "Sets a datalogger meter resolution" },
	{ "getMeterResolution", getMeterResolution, METH_NOARGS, "Returns a datalogger meter resolution" },
	{ "getTotalFlow", getTotalFlow, METH_NOARGS, "Returns the total pulses recorded during a logging session" },
	{ "resetTotalFlow", resetTotalFlow, METH_NOARGS, "Resets the total pulse count recorded during a logging session" },
        { NULL, NULL, 0, NULL }
};

PyMODINIT_FUNC initLogger(void)
{
        Py_InitModule3("Logger", methods, "Python Module written in C for interacting with specific external hardware");
}
