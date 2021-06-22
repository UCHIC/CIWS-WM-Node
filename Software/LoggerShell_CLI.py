import subprocess
import os
import Logger
import requests
import arduinoHandler
import smbus

import piHandler

Logger.init()

print(" ")
print("======================== LoggerShell ========================")
print("|                                                           |")
print("| Welcome to the LoggerShell Command-Line Interface         |")
print("| Type help for a list of commands                          |")
print("|                                                           |")
print("=============================================================")
print(" ")

while(True):											# Run LoggerShell until the exit flag is set
	print("> ")
	userInput = input("> ")

	if(userInput == "get-battery-voltage"):									# User Option: Read the battery voltage
		try:
			bus = smbus.SMBus(1)
			bus.write_byte(0x68, 0x10)
			data = bus.read_i2c_block_data(0x68, 0x00, 2)
			raw_adc = (data[0] & 0x0F) * 256 + data[1]
			if raw_adc > 2047:
				raw_adc -= 4095
			print("> Battery voltage:", round(raw_adc * .0075, 2))						# Get the battery voltage and display it
		except:
			print("> Battery voltage: <ADC Error> Note: Have you enabled I2C in raspi-config?")								#If exception print error

	elif(userInput == "internet-status"):
		try:
			requests.get('https://engineering.usu.edu/cee/people/faculty/horsburgh-jeff', timeout=5)	#Try to reach Jeffs page
			print('> Internet Status: Connected')								#Print that internet is connected
		except:
			print('> Internet Status: Not Connected')							#Print not connected

	elif(userInput == "start-logging"):									# User Option: Start a logging session										# Extract the output
		if arduinoHandler.getArduinoReport()['isLogging']:										# If the logging field is 1
			print("> Device already logging")									# Notify the user that the device is already logging
		else:													# Else
			print("> Setting start bit...")										# Notify the user that a logging session is being started
			arduinoHandler.startLogging()										# Run the sub-process (This one starts a logging session)
			print("> Checking start bit...")										# Notify the user that the start bit is being checked
			logging = arduinoHandler.getArduinoReport()['isLogging']										# Extract the output
			if logging:										# If the logging field is 1
				print("> Logging started successfully")									# Notify the user that a logging session was successfully started
			else:													# Else
				print("> Logging was not started, logging field == ", logging)					# Notify the user that a logging session was not successfully started

	elif(userInput == "stop-logging"):									# User Option: Stop a logging session
		if not arduinoHandler.getArduinoReport()['isLogging']:										# If the logging field is 0
			print("> Device is not logging")										# Notify the user that the device is already not logging
		else:													# Else
			print("> Setting stop bit...")										# Notify the user that the logging session is being stopped
			arduinoHandler.stopLogging()										# Run the sub-process
			print("> Reading EEPROM...")										# Notify the user that the EEPROM is being read
			arduinoHandler.writeEEPROMToFile()
			piHandler.processData()
			print("> Checking stop bit...")										# Notify the user that the stop bit is being checked
			logging = arduinoHandler.getArduinoReport()['isLogging']										# Extract the output
			if not logging:										# If the logging field is 0
				print("> Logging stopped successfully")									# Notify the user that a logging session was successfully stopped
			else:													# Else
				print("> Logging was not stopped, logging field == ", logging)					# Notify the user that a logging session was not successfully stopped

	elif(userInput == "date-time"):										# User Option: Display the current date and time
		outputList = arduinoHandler.getArduinoReport()
		print(">", str(outputList['month']).zfill(2) + "/" + str(outputList['day']).zfill(2) + "/" + "20" + str(outputList['year']).zfill(2))												# Display date
		print(">", str(outputList['hour']).zfill(2) + ":" + str(outputList['minute']).zfill(2) + ":" + str(outputList['second']).zfill(2))												# Display time

	elif(userInput == "set-date-time"):									# User Option: Update the date and time information on the microcontroller
		newMonth = int(input("> Month (mm): "))									# Prompt user to input the current month
		newDay = int(input("> Day (dd): "))									# Prompt user to input the current day
		newYear = int(input("> Year (yy): "))									# Prompt user to input the current year
		newHour = int(input("> Hour (hh): "))									# Prompt user to input the current hour
		newMinute = int(input("> Minute (mm): "))								# Prompt user to input the current minute
		newSecond = int(input("> Second (ss): "))								# Prompt user to input the current second
															# Command to set a new date and time
		arduinoHandler.setDateTime(newYear, newMonth, newDay, newHour, newMinute, newSecond)
		outputList = arduinoHandler.getArduinoReport()
		print(">", str(outputList['month']).zfill(2) + "/" + str(outputList['day']).zfill(2) + "/" + "20" + str(outputList['year']).zfill(2))												# Display date
		print(">", str(outputList['hour']).zfill(2) + ":" + str(outputList['minute']).zfill(2) + ":" + str(outputList['second']).zfill(2))

	elif(userInput == "set-timer-resolution"):									# User Option: Set a clock period (the time interval between data records is controlled by a timer period in the RTC)
		print("> WARNING: Changing the clock period during a logging session will corrupt timestamps.")		# Warn the user that this action should not be done during a logging session
		newPeriod = input("> New Period (integer value between 1 and 254) or C to CANCEL: ")		# Prompt the user for a new period (or cancel)
		if(newPeriod != "C"):											# If the user decided not to cancel
			arduinoHandler.setTimerResolution(int(newPeriod))
			period = arduinoHandler.getArduinoReport()['period']										# Extract the new period from the output list
			piHandler.writeConfig('Period', period)									# Store the new period in a file
			print("> Period Set:", period)									# Display the newly set period to the user
		else:													# Else
			print("> Period unchanged")										# Notify the user that the period was not changed

	elif(userInput == "get-timer-resolution"):									# User Option: Display the set clock period									# Update the period on-file to match
		print("> Period:", piHandler.readConfig('Period'))

	elif(userInput == "set-id"):										# User Option: Set a new ID number for the device									# Prompt the user for a new ID number
		piHandler.writeConfig('ID', input("> New ID: "))											# Store the new ID number in a file

	elif(userInput == "get-id"):										# User Option: Retrieve the current ID number for the device
		print("> Datalogger ID:", piHandler.readConfig('ID'))									# Display the current ID number

	elif(userInput == "set-site"):										# User Option: Set a new site number for the device								# Prompt the user for a new site number
		piHandler.writeConfig('Site', input("> New Site: "))										# Store the site number in a file

	elif(userInput == "get-site"):										# User Option: Retrieve the current site number for the device
		print("> Datalogger Site:", piHandler.readConfig('Site'))									# Display the current site number

	elif(userInput == "set-meter-resolution"):										# User Option: Set a new meter resolution for the device						# Prompt the user for a new meter resolution
		piHandler.writeConfig('meterResolution', input("> New Meter Resolution: "))									# Store the meter resolution in a file

	elif(userInput == "get-meter-resolution"):										# User Option: Retrieve the current meter resolution for the device
		print("> Meter Resolution:", piHandler.readConfig('meterResolution'))									# Display the current meter resolution

	elif(userInput == "set-transmission"):									# User Option: Setting for which data set to transmit
		print("> 0 - No transmission")
		print("> 1 - Only transmit raw data")									# Display options to user
		print("> 2 - Only transmit disaggregated data")
		print("> 3 - Transmit all data")							# Prompt user for setting
		piHandler.writeConfig('Transmission', input("> New Transmission: "))									# Save setting

	elif(userInput == "get-transmission"):									# User Option: Display setting for which data set to transmit
		print("> 0 - No transmission")
		print("> 1 - Only transmit raw data")									# Display options to user
		print("> 2 - Only transmit disaggregated data")
		print("> 3 - Transmit all data")						# Display error if error occurs
		print("> Transmission Setting:", piHandler.readConfig('Transmission'))								# Display transmission setting to user

	elif(userInput == "set-storage"):									# User Option: Setting for which data set to store
		print("> 1 - Only store raw data")									# Display options to user
		print("> 2 - Only store disaggregated data")
		print("> 3 - Store all data")								# Prompt user for setting
		piHandler.writeConfig('Storage', input("> New data storage: "))										# Save setting

	elif(userInput == "get-storage"):									# User Option: Display setting for which data set to store
		print("> 1 - Only store raw data")									# Display options to user
		print("> 2 - Only store disaggregated data")
		print("> 3 - Store all data")						# Display error if error occurs
		print("> Data storage setting:", piHandler.readConfig('Storage'))								# Display data storage setting to user

	elif(userInput == "water-flow"):									# User Option: Display current water flow information
		data = arduinoHandler.getArduinoReport()										# Extract the output
		pulseCount = int(data['lastPeriodPulses'])										# Retrieve previous period's pulse count
		totalCount = (int(data['totalPulses1']) << 16) + (int(data['totalPulses2']) << 8) + int(data['totalPulses3'])		# Retrieve total pulse count (for logging session)
		meterResolution = piHandler.readConfig('meterResolution')								# Retrieve the meter resolution
		if(meterResolution == 0):										# If the meter resolution is zero:
			print("> WARNING: Error reading meter resolution.")							# Warn the user that the meter resolution was not properly read.
		waterFlow = pulseCount * float(meterResolution) * 60.0 / 4.0						# Estimate water flow from previous period based on pulse count and meter resolution
		totalWaterFlow = float(totalCount) * float(meterResolution)						# Estimate total water flow based on total pulse count and meter resolution
		print("> Pulses in last period:", pulseCount)								# Display pulse count from previous period
		print("> Estimated water flow:", waterFlow, "GPM")							# Display estimated water flow from previous period
		print("> Total pulses counted:", totalCount)								# Display total pulse count from current logging session
		print("> Total water volume:", totalWaterFlow, "Gal")							# Display estimated total water flow from current logging session

	elif(userInput == "help"):										# User Option: Display the help menu
		print("> LoggerShell is a shell interface for all of the")						# Print a list of commands with a brief description of each
		print("> functionality between the Raspberry Pi and the")
		print("> datalogging microcontroller. The following is a list")
		print("> of commands:")
		print(">")
		print("> date-time             // Displays the current date/time")
		print("> set-date-time         // Updates the current date/time")
		print("> set-timer-resolution  // Sets the time interval between samples")
		print("> get-timer-resolution  // Displays the time interval between samples")
		print("> exit                  // Exit from LoggerShell")
		print("> exit-poweroff         // Exit from LoggerShell and power off (Microcontroller will continue to log data)")
		print("> start-logging         // Begin logging data")
		print("> stop-logging          // Stop logging data")
		print("> set-id                // Set a new datalogger ID number")
		print("> get-id                // Read and display the datalogger ID number")
		print("> set-site              // Set a new datalogger site number")
		print("> get-site              // Read and display the datalogger site number")
		print("> set-meter-resolution  // Set a meter resolution for the datalogger")
		print("> get-meter-resolution  // Read and display the meter resolution for the datalogger")
		print("> set-transmission      // Change data transmission setting")
		print("> get-transmission      // Read and display transmission setting")
		print("> set-storage           // Change data storage setting")
		print("> get-storage           // Read and display storage setting")
		print("> get-battery-voltage   // Display battery voltage")
		print("> internet-status       // Checks if node is connected to the internet")
		print("> water-flow            // Display water flow data for the previous sample")

	elif(userInput == "exit"):										# User Option: Exit LoggerShell
		print("> To restart LoggerShell, execute the following command: sudo python3 LoggerShell_CLI.py")		# Inform the user how to restart LoggerShell
		break												# Set the exit flag to 1

	elif(userInput == "exit-poweroff"):									# User Option: Exit LoggerShell and power down the Raspberry Pi (microcontroller continues to log data)											# Set the exit flag to 1
		os.system("sudo poweroff")												# Set the powerOff flag to 1

	else:													# Handle invalid input
		print("> Invalid input. Type help for a list of commands.")						# Notify the user that the command was invalid

print("> Done")												# Notify the user that LoggerShell is exiting
