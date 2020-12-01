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
	unsigned char recordNum = (data[4] << 16) + (data[5] << 8) + data[6];	// Calculate number of records stored
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
