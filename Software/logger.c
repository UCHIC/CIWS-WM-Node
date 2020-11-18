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
#define BUFFER_MAX  24000
#define HEADER_SIZE 9

#define START 0xEE

#define REPORT_SIZE 12

int serialFD;	// File pointer for the UART

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

	unsigned int lastIndex = recordNum + HEADER_SIZE + 3; //recordNum + HEADER_SIZE + 4;	// lastIndex points to the last record stored in data[]
	if(lastIndex > dataSize)
		lastIndex = dataSize;

	PyObject* dataTuple = PyTuple_New(recordNum + 7);	// The dataTuple is what will be used in the Python script Logger is used in.

	PyObject* PyData = Py_BuildValue("B", recordNum);	// To store data in dataTuple, we need a PyObject.

	PyTuple_SetItem(dataTuple, 0, PyData);			// The first value in dataTuple is the number of records it holds.

	unsigned int i;
	for(i = 7; i <= lastIndex; i++)				// This loop fills dataTuple with date/time and records.
	{
		PyData = Py_BuildValue("B", data[i]);
		PyTuple_SetItem(dataTuple, i - 6, PyData);
	}

	return dataTuple;					// dataTuple is returned for use in a Python script
}

/** Exchange Reports with the AVR datalogger **/

static PyObject* reportSwap(PyObject* self, PyObject* args)
{
	PyObject* PyReport;

	int i;
	char report[REPORT_SIZE];

	if(!PyArg_ParseTuple(args, "O!", &PyList_Type, &PyReport))			// Parse arguments for PyReport
	{
		PyErr_SetString(PyExc_TypeError, "Parameter must be a list.");			// If parse fails, set error and return
		return NULL;
	}
	serialPutchar(serialFD, START);							// Send START byte
	for(i = 0; i < REPORT_SIZE; i++)						// Iterate over all report data in PyReport
	{
		report[i] = (char)PyLong_AsLong(PyList_GetItem(PyReport, i));		// Extract data byte from PyReport
		serialPutchar(serialFD, report[i]);						// Send data byte
		report[i] = (char)serialGetchar(serialFD);					// Receive data byte
		PyList_SetItem(PyReport, i, Py_BuildValue("b", report[i]));			// Store data byte in PyReport
	}

	return PyReport;								// Return report data
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
	if(!PyArg_ParseTuple(args, "Os", &DataList, &filename))		// Retrieve the data and put it into DataList.
	{
		PyErr_SetString(PyExc_TypeError, "Expected a list and a string.");	// If the operation fails, set an error and return.
		return PyUnicode_FromString("Bad arguments");
	}

	FILE* clockPeriod;
	int deltaSec = 0;
	clockPeriod = fopen("/home/pi/Software/config/clockPeriod.txt", "r");		// Open the clock period file
	if(clockPeriod == NULL)								// Check file
	{
		PyErr_SetString(PyExc_TypeError, "Could not open clockPeriod.txt.");
		return PyUnicode_FromString("Could not open clockPeriod.txt.");
	}
	int scan = fscanf(clockPeriod, "%d", &deltaSec);				// Store the clock period as deltaSec
	if(scan == 0)
	{
		PyErr_SetString(PyExc_TypeError, "Error reading clockPeriod.txt.");
                return PyUnicode_FromString("Error reading clockPeriod.txt.");
	}
	fclose(clockPeriod);

	FILE* IDconfig;
	char IDnum[] = {0, 0, 0, 0, 0};
	IDconfig = fopen("/home/pi/Software/config/IDconfig.txt", "r");			// Open the ID file
	if(IDconfig == NULL)								// Check file
	{
		PyErr_SetString(PyExc_TypeError, "Could not open IDconfig.txt.");
		return PyUnicode_FromString("Could not open IDconfig.txt.");
	}
	scan = fscanf(IDconfig, "%4s", IDnum);						// Store the ID as IDnum
	if(scan == 0)
	{
		PyErr_SetString(PyExc_TypeError, "Error reading IDconfig.txt.");
                return PyUnicode_FromString("Error reading IDconfig.txt.");
	}
	fclose(IDconfig);

	FILE* siteConfig;
	char siteNum[] = {0, 0, 0, 0, 0};
	siteConfig = fopen("/home/pi/Software/config/siteConfig.txt", "r");		// Open the site file
	if(siteConfig == NULL)								// Check file
	{
		PyErr_SetString(PyExc_TypeError, "Could not open siteConfig.txt.");
		return PyUnicode_FromString("Could not open siteConfig.txt.");
	}
	scan = fscanf(siteConfig, "%4s", siteNum);					// Store the site as siteNum
	if(scan == 0)
	{
		PyErr_SetString(PyExc_TypeError, "Error reading siteConfig.txt");
		return PyUnicode_FromString("Error reading siteConfig.txt");
	}
	fclose(siteConfig);

	FILE* meterConfig;
	char meterRez[] = {0, 0, 0, 0, 0, 0, 0, 0, 0};
	meterConfig = fopen("/home/pi/Software/config/meterConfig.txt", "r");		// Open the meter file
	if(meterConfig == NULL)								// Check file
	{
		PyErr_SetString(PyExc_TypeError, "Could not open meterConfig.txt.");
		return PyUnicode_FromString("Could not open meterConfig.txt.");
	}
	scan = fscanf(meterConfig, "%8s", meterRez);					// Store meter as meterRez
	if(scan == 0)
	{
		PyErr_SetString(PyExc_TypeError, "Error reading meterConfig.txt");
		return PyUnicode_FromString("Error reading meterConfig.txt");
	}
	fclose(meterConfig);

	PyObject* Iterator = PyObject_GetIter(DataList);		// Create an iterator to traverse the contents of DataList
	if(!Iterator)
	{
		PyErr_SetString(PyExc_TypeError, "Error setting list iterator.");
		return PyUnicode_FromString("Error setting list iterators.");
	}

	dataOut = fopen(filename, "w");
	if(dataOut == NULL)						// Create new data file
	{
		PyErr_SetString(PyExc_TypeError, "Could not create file.");
		return PyUnicode_FromString("Could not create file.");
	}

	fprintf(dataOut, "Site #: %s\nDatalogger ID #: %s\nMeter Resolution: %s\n", siteNum, IDnum, meterRez);

	PyObject* next = PyIter_Next(Iterator);				// Each next holds the data from the current DataList index.

	unsigned int index = 0;
	/* Date and Time variables will be used to write timestamps in the output file */
	int month = 0;
	int day = 0;
	int year = 0;
	int hour = 0;
	int minute = 0;
	int second = 0;
	long data;
	int recordNum = 1;

	while(next != NULL)						// Print each value to the output file.
	{
		data = PyLong_AsLong(next);
		if (index < 7)							// Save starting timestamp
		{
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
		else	// Once the timestamp has been filled up, and the header has been created, write pulse data to file and calculate a new timestamp
		{
			fprintf(dataOut, "\"%02d-%02d-%02d %02d:%02d:%02d\",%d,%ld\n", year, month, day, hour, minute, second, recordNum, data);	// Print the timestamp, record number, and data.
			recordNum += 1;				// Increment the record number
			second += deltaSec;			// Increment the seconds by the time interval
			if (second >= 60)			// Update the rest of the timestamp fields accordingly
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
			if (day > 31)
			{
				day = 1;
				month += 1;
			}
			if (day > 30)
			{
				if((month == 9) || (month == 4) || (month == 6) || (month == 11))	// If Month with thirty days
				{
					day = 1;
					month += 1;
				}
			}
			if (day > 29)
			{
				if(month == 2)	// If February
				{
					day = 1;
					month += 1;
				}
			}
			if (day > 28)
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
		index += 1;				// Increment index
	}

	fclose(dataOut);				// Close the data file

	return Py_None;
}

static PyObject* storePeriod(PyObject* self, PyObject* args)
{
	FILE* clockPeriod;
	unsigned char newPeriod;
	clockPeriod = fopen("/home/pi/Software/config/clockPeriod.txt", "w");		// Open clockPeriod file
	if(clockPeriod == NULL)								// Check file
	{
		return PyUnicode_FromString("Could not open clockPeriod.txt");
	}
	if(!PyArg_ParseTuple(args, "b", &newPeriod))					// Parse arguments
	{
		PyErr_SetString(PyExc_TypeError, "Expected an eight-bit integer.");	// If parsing fails, set error and return
		return PyUnicode_FromString("Bad arguments");
	}
	fprintf(clockPeriod, "%d\n", newPeriod);					// Write new clock period
	fclose(clockPeriod);								// Close clockPeriod file

	return Py_None;
}

static PyObject* getPeriod(PyObject* self, PyObject* args)
{
	FILE* clockPeriod;
	char period[] = {0, 0, 0, 0, 0};
	clockPeriod = fopen("/home/pi/Software/config/clockPeriod.txt", "r");		// Open clockPeriod file
	if(clockPeriod == NULL)								// Check file
	{
		return Py_BuildValue("i", 0);
	}
	int scan = fscanf(clockPeriod, "%4s", period);					// Read period number
	if(scan == 0)
	{
		return Py_BuildValue("i", 0);
	}
	fclose(clockPeriod);								// Close clockPeriod file

	return PyUnicode_FromString(period);						// Return clockPeriod
}

static PyObject* setID(PyObject* self, PyObject* args)
{
	FILE* IDconfig;
	char* newID;
	IDconfig = fopen("/home/pi/Software/config/IDconfig.txt", "w");			// Open ID Config File
	if(IDconfig == NULL)								// Check file
	{
		return PyUnicode_FromString("Could not open IDconfig.txt.");
	}
	if(!PyArg_ParseTuple(args, "s", &newID))					// Parse arguments
        {
                PyErr_SetString(PyExc_TypeError, "Expected a string.");     	 	// If parsing fails, set error and return.
                return PyUnicode_FromString("Bad arguments");
        }
	fprintf(IDconfig, "%s\n", newID);						// Write new ID number
	fclose(IDconfig);

	return Py_None;									// Close ID Config File
}

static PyObject* setSiteNumber(PyObject* self, PyObject* args)
{
	FILE* siteConfig;
	char* newSite;
	siteConfig = fopen("/home/pi/Software/config/siteConfig.txt", "w");		// Open Site Config File
	if(siteConfig == NULL)								// Check file
	{
		return PyUnicode_FromString("Could not open siteConfig.txt");
	}
	if(!PyArg_ParseTuple(args, "s", &newSite))					// Parse arguments
	{
		PyErr_SetString(PyExc_TypeError, "Expected a string.");                 // If parsing fails, set error and return.
                return PyUnicode_FromString("Bad arguments");
	}
	fprintf(siteConfig, "%s\n", newSite);						// Write new Site number
	fclose(siteConfig);								// Close Site Config File

	return Py_None;
}

static PyObject* setMeterResolution(PyObject* self, PyObject* args)
{
	FILE* meterConfig;
	char* newMeterRez;
	meterConfig = fopen("/home/pi/Software/config/meterConfig.txt", "w");		// Open Meter Config File
	if(meterConfig == NULL)								// Check file
	{
		return PyUnicode_FromString("Could not open meterConfig.txt");
	}
	if(!PyArg_ParseTuple(args, "s", &newMeterRez))					// Parse arguments
	{
		PyErr_SetString(PyExc_TypeError, "Expected a string.");                 // If parsing fails, set error and return.
                return PyUnicode_FromString("Bad arguments");
	}
	fprintf(meterConfig, "%s\n", newMeterRez);					// Write new Meter Resolution
	fclose(meterConfig);								// Close Meter Config File

	return Py_None;
}

static PyObject* setTransmission(PyObject* self, PyObject* args)
{
	FILE* transmissionConfig;
	char* newTransmissionSetting;
	transmissionConfig = fopen("/home/pi/Software/config/transmissionConfig.txt", "w");	// Open transmission config file
	if(transmissionConfig == NULL)								// Check file
	{
		return PyUnicode_FromString("Could not open transmissionConfig.txt");
	}
	if(!PyArg_ParseTuple(args, "s", &newTransmissionSetting))				// Parse arguments
	{
		PyErr_SetString(PyExc_TypeError, "Expected a string.");				// If parsing fails, set error and return.
		return PyUnicode_FromString("Bad arguments");
	}
	fprintf(transmissionConfig, "%s\n", newTransmissionSetting);				// Write new transmission setting
	fclose(transmissionConfig);								// Close transmission config file

	return Py_None;
}

static PyObject* setStorage(PyObject* self, PyObject* args)
{
	FILE* dataStoreConfig;
	char* newDataStore;
	dataStoreConfig = fopen("/home/pi/Software/config/dataStoreConfig.txt", "w");		// Open data storage config file
	if(dataStoreConfig == NULL)								// Check file
	{
		return PyUnicode_FromString("Could not open dataStoreConfig.txt");
	}
	if(!PyArg_ParseTuple(args, "s", &newDataStore))						// Parse arguments
	{
		PyErr_SetString(PyExc_TypeError, "Expected a string.");				// If parsing fails, set error and return
		return PyUnicode_FromString("Bad arguments");
	}
	fprintf(dataStoreConfig, "%s\n", newDataStore);						// Write new data storage setting
	fclose(dataStoreConfig);								// Close data storage config file

	return Py_None;
}

static PyObject* getTransmission(PyObject* self, PyObject* args)
{
	FILE* transmissionConfig;
	char transmissionSetting[] = {0, 0};
	transmissionConfig = fopen("/home/pi/Software/config/transmissionConfig.txt", "r");	// Open transmission config file
	if(transmissionConfig == NULL)								// Check file
	{
		return Py_BuildValue("i", 0);
	}
	int scan = fscanf(transmissionConfig, "%s", transmissionSetting);			// Read transmission setting
	if(scan == 0)
	{
		return Py_BuildValue("i", 0);
	}
	fclose(transmissionConfig);								// Close transmission config file

	return PyUnicode_FromString(transmissionSetting);					// Return transmission setting
}

static PyObject* getStorage(PyObject* self, PyObject* args)
{
	FILE* dataStoreConfig;
	char dataStore[] = {0, 0};
	dataStoreConfig = fopen("/home/pi/Software/config/dataStoreConfig.txt", "r");		// Open data storage config file
	if(dataStoreConfig == NULL)								// Check file
	{
		return Py_BuildValue("i", 1);
	}
	int scan = fscanf(dataStoreConfig, "%s", dataStore);					// Read data storage setting
	if(scan == 0)
	{
		return Py_BuildValue("i", 1);
	}
	fclose(dataStoreConfig);								// Close data storage config file

	return PyUnicode_FromString(dataStore);							// Return data storage setting
}

static PyObject* getID(PyObject* self, PyObject* args)
{
	FILE* IDconfig;
	char IDnum[] = {0, 0, 0, 0, 0};
	IDconfig = fopen("/home/pi/Software/config/IDconfig.txt", "r");			// Open ID config file
	if(IDconfig == NULL)								// Check file
	{
		return Py_BuildValue("i", 0);
	}
	int scan = fscanf(IDconfig, "%4s", IDnum);					// Read ID number
	if(scan == 0)
	{
		return Py_BuildValue("i", 0);
	}
	fclose(IDconfig);								// Close ID config file

	return PyUnicode_FromString(IDnum);						// Return ID number
}

static PyObject* getSiteNumber(PyObject* self, PyObject* args)
{
	FILE* siteConfig;
	char siteNum[] = {0, 0, 0, 0, 0};
	siteConfig = fopen("/home/pi/Software/config/siteConfig.txt", "r");		// Open Site config file
	if(siteConfig == NULL)								// Check file
	{
		return Py_BuildValue("i", 0);
	}
	int scan = fscanf(siteConfig, "%4s", siteNum);					// Read site number
	if(scan == 0)
	{
		return Py_BuildValue("i", 0);
	}
	fclose(siteConfig);								// Close site config file

	return PyUnicode_FromString(siteNum);						// Return site number
}

static PyObject* getMeterResolution(PyObject* self, PyObject* args)
{
	FILE* meterConfig;
	char meterRez[] = {0, 0, 0, 0, 0, 0, 0, 0, 0};
	meterConfig = fopen("/home/pi/Software/config/meterConfig.txt", "r");		// Open meter config file
	if(meterConfig == NULL)								// Check file
	{
		return Py_BuildValue("i", 0);
	}
	int scan = fscanf(meterConfig, "%8s", meterRez);				// Read meter resolution
	if(scan == 0)
	{
		return Py_BuildValue("i", 0);
	}
	fclose(meterConfig);								// Close meter config file

	return PyUnicode_FromString(meterRez);						// Return meter resolution
}

/* Used by python build script to compile Logger module */
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
	{ "storePeriod", storePeriod, METH_VARARGS, "Stores a configured clock period to file" },
	{ "getPeriod", getPeriod, METH_NOARGS, "Returns the time interval between samples" },
	{ "setID", setID, METH_VARARGS, "Sets a datalogger ID number" },
	{ "setSiteNumber", setSiteNumber, METH_VARARGS, "Sets a datalogger site number" },
	{ "setTransmission", setTransmission, METH_VARARGS, "Sets data transmission settings" },
	{ "setStorage", setStorage, METH_VARARGS, "Sets data storage settings" },
	{ "getTransmission", getTransmission, METH_NOARGS, "Reads data transmission settings" },
	{ "getStorage", getStorage, METH_NOARGS, "Reads data storage settings" },
	{ "getID", getID, METH_NOARGS, "Returns a datalogger ID number" },
	{ "getSiteNumber", getSiteNumber, METH_NOARGS, "Returns a datalogger site number" },
	{ "setMeterResolution", setMeterResolution, METH_VARARGS, "Sets a datalogger meter resolution" },
	{ "getMeterResolution", getMeterResolution, METH_NOARGS, "Returns a datalogger meter resolution" },
    { NULL, NULL, 0, NULL }
};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "Logger",
    "Module used to communicate with Arduino.",
    -1,
    methods,
    NULL,
    NULL,
    NULL,
    NULL,
};

/* Used by python build script to compile Logger module */
PyMODINIT_FUNC PyInit_Logger(void)
{
        return PyModule_Create(&moduledef);
}
