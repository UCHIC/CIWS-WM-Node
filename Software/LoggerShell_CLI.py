import subprocess
import os
import Logger
from MCP3425 import getVoltage

exit = 0
powerOff = 0
command = ["-", "-", "-"]
Logger.init()

print(" ")
print("======================== LoggerShell ========================")
print("|                                                           |")
print("| Welcome to the LoggerShell Command-Line Interface         |")
print("| Type help for a list of commands                          |")
print("|                                                           |")
print("=============================================================")
print(" ")

while(exit == 0):											# Run LoggerShell until the exit flag is set
	print("> ")
	userInput = input("> ")

	if(userInput == "get-battery-voltage"):									# User Option: Read the battery voltage
		try:
			print("> Battery voltage: ", getVoltage())								# Get the battery voltage and display it
		except:
			print("> Battery voltage: <ADC Error>")

	elif(userInput == "start-logging"):									# User Option: Start a logging session
		command[0] = "python3 LoggerReportSwap.py 255 255 255 255 255 255 255 255 255 255 255 255"		# Command to read report data
		command[1] = "python3 LoggerReportSwap.py 255 255 255 255 255 255 255 255 255 255 1 255"			# Command to start a logging session
		process = subprocess.Popen(command[0], stdout=subprocess.PIPE, shell=True)				# Create a sub-process to run command[0]
		(output, err) = process.communicate()									# Assign variables in which to store output
		p_status = process.wait()										# Run the sub-process
		outputList = output.split()										# Extract the output
		if(int(outputList[10]) == 1):										# If the logging field is 1
			print("> Device already logging")									# Notify the user that the device is already logging
		else:													# Else
			print("> Setting start bit...")										# Notify the user that a logging session is being started
			process = subprocess.Popen(command[1], stdout=subprocess.PIPE, shell=True)				# Create a sub-process to run command[1]
			(output, err) = process.communicate()									# Assign variables in which to store output
			p_status = process.wait()										# Run the sub-process (This one starts a logging session)
			print("> Checking start bit...")										# Notify the user that the start bit is being checked
			process = subprocess.Popen(command[0], stdout=subprocess.PIPE, shell=True)				# Create a sub-process to run command[0]
			(output, err) = process.communicate()									# Assign variables in which to store output
			p_status = process.wait()										# Run the sub-process (This one checks to see if command[1] was successful)
			outputList = output.split()										# Extract the output
			if(int(outputList[10]) == 1):										# If the logging field is 1
				print("> Logging started successfully")									# Notify the user that a logging session was successfully started
			else:													# Else
				print("> Logging was not started, logging field == ", outputList[10])					# Notify the user that a logging session was not successfully started

	elif(userInput == "stop-logging"):									# User Option: Stop a logging session
		command[0] = "python3 LoggerReportSwap.py 255 255 255 255 255 255 255 255 255 255 255 255"		# Command to read report data
		command[1] = "python3 LoggerReportSwap.py 255 255 255 255 255 255 255 255 255 255 0 255"			# Command to stop a logging session
		command[2] = "python3 LoggerReadRom.py"									# Command to read the EEPROM chip (to obtain remaining data in logging session)
		process = subprocess.Popen(command[0], stdout=subprocess.PIPE, shell=True)				# Create a sub-process to run command[0]
		(output, err) = process.communicate()									# Assign variables in which to store output
		p_status = process.wait()										# Run the sub-process
		outputList = output.split()										# Extract the output
		if(int(outputList[10]) == 0):										# If the logging field is 0
			print("> Device is not logging")										# Notify the user that the device is already not logging
		else:													# Else
			print("> Setting stop bit...")										# Notify the user that the logging session is being stopped
			process = subprocess.Popen(command[1], stdout=subprocess.PIPE, shell=True)				# Create a sub-process to run command[1]
			(output, err) = process.communicate()									# Assign variables in which to store output
			p_status = process.wait()										# Run the sub-process
			print("> Reading EEPROM...")										# Notify the user that the EEPROM is being read
			process = subprocess.Popen(command[2], stdout=subprocess.PIPE, shell=True)				# Create a sub-process to run command[2]
			(output, err) = process.communicate()									# Assign variables in which to store the output
			p_status = process.wait()										# Run the sub-process
			print("> Checking stop bit...")										# Notify the user that the stop bit is being checked
			process = subprocess.Popen(command[0], stdout=subprocess.PIPE, shell=True)				# Create a sub-process to run command[0]
			(output, err) = process.communicate()									# Assign variables in which to store the output
			p_status = process.wait()										# Run the sub-process
			outputList = output.split()										# Extract the output
			if(int(outputList[10]) == 0):										# If the logging field is 0
				print("> Logging stopped successfully")									# Notify the user that a logging session was successfully stopped
			else:													# Else
				print("> Logging was not stopped, logging field == ", outputList[10])					# Notify the user that a logging session was not successfully stopped

	elif(userInput == "date-time"):										# User Option: Display the current date and time
		command[0] = "python3 LoggerReportSwap.py 255 255 255 255 255 255 255 255 255 255 255 255"		# Command to read report data
		process = subprocess.Popen(command[0], stdout=subprocess.PIPE, shell=True)				# Create a sub-process to run command[0]
		(output, err) = process.communicate()									# Assign variables in which to store output
		p_status = process.wait()										# Run the sub-process
		outputList = output.split()										# Extract the output
		Date = outputList[1].decode().zfill(2) + "/" + outputList[2].decode().zfill(2) + "/" + "20" + outputList[0].decode().zfill(2)	# Format date information
		Time = outputList[3].decode().zfill(2) + ":" + outputList[4].decode().zfill(2) + ":" + outputList[5].decode().zfill(2)		# Format time information
		print(">", Date)												# Display date
		print(">", Time)												# Display time

	elif(userInput == "update-date-time"):									# User Option: Update the date and time information on the microcontroller
		newMonth = input("> Month (mm): ")									# Prompt user to input the current month
		newDay = input("> Day (dd): ")									# Prompt user to input the current day
		newYear = input("> Year (yy): ")									# Prompt user to input the current year
		newHour = input("> Hour (hh): ")									# Prompt user to input the current hour
		newMinute = input("> Minute (mm): ")								# Prompt user to input the current minute
		newSecond = input("> Second (ss): ")								# Prompt user to input the current second
		space = " "
															# Command to set a new date and time
		command[0] = "python3 LoggerReportSwap.py " + newYear + space + newMonth + space + newDay + space + newHour + space + newMinute + space + newSecond + " 255 255 255 255 255 255"
		command[1] = "python3 LoggerReportSwap.py 255 255 255 255 255 255 255 255 255 255 255 255"		# Command to read report data
		process = subprocess.Popen(command[0], stdout=subprocess.PIPE, shell=True)				# Create a sub-process to run command[0]
		(output, err) = process.communicate()									# Assign variables in which to store output
		p_status = process.wait()										# Run the sub-process
		process = subprocess.Popen(command[1], stdout=subprocess.PIPE, shell=True)				# Create a sub-process to run command[1]
		(output, err) = process.communicate()									# Assign variables in which to store output
		p_status = process.wait()										# Run the sub-process
		outputList = output.split()										# Extract the output
		Date = outputList[1].decode().zfill(2) + "/" + outputList[2].decode().zfill(2) + "/" + "20" + outputList[0].decode().zfill(2)	# Display date
		Time = outputList[3].decode().zfill(2) + ":" + outputList[4].decode().zfill(2) + ":" + outputList[5].decode().zfill(2)		# Display time
		print(">", Date)
		print(">", Time)

	elif(userInput == "set-clock-period"):									# User Option: Set a clock period (the time interval between data records is controlled by a timer period in the RTC)
		print("> WARNING: Changing the clock period during a logging session will corrupt timestamps.")		# Warn the user that this action should not be done during a logging session
		newPeriod = input("> New Period (integer value between 1 and 254) or C to CANCEL: ")		# Prompt the user for a new period (or cancel)
		if(newPeriod != "C"):											# If the user decided not to cancel
			command[0] = "python3 LoggerReportSwap.py 255 255 255 255 255 255 255 255 255 255 255 " + newPeriod	# Command to set the new period
			command[1] = "python3 LoggerReportSwap.py 255 255 255 255 255 255 255 255 255 255 255 255"		# Command to read report data
			process = subprocess.Popen(command[0], stdout=subprocess.PIPE, shell=True)				# Create a sub-process to run command[0]
			(output, err) = process.communicate()									# Assign variables in which to store output
			p_status = process.wait()										# Run the sub-process
			process = subprocess.Popen(command[1], stdout=subprocess.PIPE, shell=True)				# Create a sub-process to run command[1]
			(output, err) = process.communicate()									# Assign variables in which to store output
			p_status = process.wait()										# Run the sub-process
			outputList = output.split()										# Extract the output
			newPeriod = outputList[11]										# Extract the new period from the output list
			Logger.storePeriod(int(newPeriod))									# Store the new period in a file
			print("> Period Set:", newPeriod.decode())									# Display the newly set period to the user
		else:													# Else
			print("> Period unchanged")										# Notify the user that the period was not changed

	elif(userInput == "get-clock-period"):									# User Option: Display the set clock period
		command[0] = "python3 LoggerReportSwap.py 255 255 255 255 255 255 255 255 255 255 255 255"		# Command to read report data
		process = subprocess.Popen(command[0], stdout=subprocess.PIPE, shell=True)				# Create a sub-process to run command[0]
		(output, err) = process.communicate()									# Assign variables in which to store output
		p_status = process.wait()										# Run the sub-process
		outputList = output.split()										# Extract the output
		report_period = int(outputList[11])									# Extract the period from the output list
		try:
			stored_period = int(Logger.getPeriod())									# Read the period stored on file
		except:
			stored_period = 0
		if(report_period != stored_period):									# If the period values do not match:
			Logger.storePeriod(report_period)									# Update the period on-file to match
		print("> Period:", report_period)

	elif(userInput == "set-id"):										# User Option: Set a new ID number for the device
		newID = input("> New ID: ")										# Prompt the user for a new ID number
		Logger.setID(newID)											# Store the new ID number in a file

	elif(userInput == "get-id"):										# User Option: Retrieve the current ID number for the device
		try:
			ID = Logger.getID()											# Read the current ID number from a file
		except:
			ID = "Error reading ID"
		print("> Datalogger ID:", ID)										# Display the current ID number

	elif(userInput == "set-site"):										# User Option: Set a new site number for the device
		newSite = input("> New Site: ")									# Prompt the user for a new site number
		Logger.setSiteNumber(newSite)										# Store the site number in a file

	elif(userInput == "get-site"):										# User Option: Retrieve the current site number for the device
		try:
			site = Logger.getSiteNumber()										# Read the current site number from a file
		except:
			site = "Error reading site"
		print("> Datalogger Site:", site)									# Display the current site number

	elif(userInput == "set-meter"):										# User Option: Set a new meter resolution for the device
		newMeterRez = input("> New Meter Resolution: ")							# Prompt the user for a new meter resolution
		Logger.setMeterResolution(newMeterRez)									# Store the meter resolution in a file

	elif(userInput == "get-meter"):										# User Option: Retrieve the current meter resolution for the device
		try:
			meterRez = Logger.getMeterResolution()									# Read the current meter resolution from a file
		except:
			meterRez = "Error reading meter resolution"
		print("> Meter Resolution:", meterRez)									# Display the current meter resolution

	elif(userInput == "set-transmission"):									# User Option: Setting for which data set to transmit
		print("> 0 - No transmission")
		print("> 1 - Only transmit raw data")									# Display options to user
		print("> 2 - Only transmit disaggregated data")
		print("> 3 - Transmit all data")
		transmission = input("> New Transmission: ")							# Prompt user for setting
		Logger.setTransmission(transmission)									# Save setting

	elif(userInput == "get-transmission"):									# User Option: Display setting for which data set to transmit
		print("> 0 - No transmission")
		print("> 1 - Only transmit raw data")									# Display options to user
		print("> 2 - Only transmit disaggregated data")
		print("> 3 - Transmit all data")
		try:
			transmission = Logger.getTransmission()								# Retrieve saved setting
		except:
			transmission = "Error reading transmission settings"						# Display error if error occurs
		print("> Transmission Setting:", transmission)								# Display transmission setting to user

	elif(userInput == "set-storage"):									# User Option: Setting for which data set to store
		print("> 1 - Only store raw data")									# Display options to user
		print("> 2 - Only store disaggregated data")
		print("> 3 - Store all data")
		dataStore = input("> New data storage: ")								# Prompt user for setting
		Logger.setStorage(dataStore)										# Save setting

	elif(userInput == "get-storage"):									# User Option: Display setting for which data set to store
		print("> 1 - Only store raw data")									# Display options to user
		print("> 2 - Only store disaggregated data")
		print("> 3 - Store all data")
		try:
			dataStore = Logger.getStorage()								# Retrieve saved setting
		except:
			dataStore = "Error reading data storage settings"						# Display error if error occurs
		print("> Data storage setting:", dataStore)								# Display data storage setting to user

	elif(userInput == "water-flow"):									# User Option: Display current water flow information
		command[0] = "python3 LoggerReportSwap.py 255 255 255 255 255 255 255 255 255 255 255 255"		# Command to read report data
		process = subprocess.Popen(command[0], stdout=subprocess.PIPE, shell=True)				# Create a sub-process to run command[0]
		(output, err) = process.communicate()									# Assign variables in which to store output
		p_status = process.wait()										# Run the sub-process
		outputList = output.split()										# Extract the output
		pulseCount = int(outputList[6])										# Retrieve previous period's pulse count
		totalCount = (int(outputList[7]) << 16) + (int(outputList[8]) << 8) + int(outputList[9])		# Retrieve total pulse count (for logging session)
		meterResolution = Logger.getMeterResolution()								# Retrieve the meter resolution
		if(meterResolution == 0):										# If the meter resolution is zero:
			print("> WARNING: Error reading meter resolution.")							# Warn the user that the meter resolution was not properly read.
		waterFlow = pulseCount * float(meterResolution) * 60.0 / 4.0						# Estimate water flow from previous period based on pulse count and meter resolution
		totalWaterFlow = float(totalCount) * float(meterResolution)						# Estimate total water flow based on total pulse count and meter resolution
		print("> Pulses in last period:", pulseCount)								# Display pulse count from previous period
		print("> Estimated water flow:", waterFlow, "GPM")							# Display estimated water flow from previous period
		print("> Total pulses counted:", totalCount)								# Display total pulse count from current logging session
		print("> Total water flow:", totalWaterFlow, "Gal")							# Display estimated total water flow from current logging session

	elif(userInput == "help"):										# User Option: Display the help menu
		command[0] = "-"
		print("> LoggerShell is a shell interface for all of the")						# Print a list of commands with a brief description of each
		print("> functionality between the Raspberry Pi and the")
		print("> datalogging microcontroller. The following is a list")
		print("> of commands:")
		print(">")
		print("> date-time             // Displays the current date/time")
		print("> update-date-time      // Updates the current date/time")
		print("> set-clock-period      // Sets the time interval between samples")
		print("> get-clock-period      // Displays the time interval between samples")
		print("> exit                  // Exit from LoggerShell")
		print("> exit-poweroff         // Exit from LoggerShell and power off (Microcontroller will continue to log data)")
		print("> start-logging         // Begin logging data")
		print("> stop-logging          // Stop logging data")
		print("> set-id                // Set a new datalogger ID number")
		print("> get-id                // Read and display the datalogger ID number")
		print("> set-site              // Set a new datalogger site number")
		print("> get-site              // Read and display the datalogger site number")
		print("> set-meter             // Set a meter resolution for the datalogger")
		print("> get-meter             // Read and display the meter resolution for the datalogger")
		print("> set-transmission      // Change data transmission setting")
		print("> get-transmission      // Read and display transmission setting")
		print("> set-storage           // Change data storage setting")
		print("> get-storage           // Read and display storage setting")
		print("> get-battery-voltage   // Display battery voltage")
		print("> water-flow            // Display water flow data for the previous sample")

	elif(userInput == "exit"):										# User Option: Exit LoggerShell
		command[0] = "-"
		print("> To restart LoggerShell, execute the following command: sudo python LoggerShell_CLI.py")		# Inform the user how to restart LoggerShell
		exit = 1												# Set the exit flag to 1

	elif(userInput == "exit-poweroff"):									# User Option: Exit LoggerShell and power down the Raspberry Pi (microcontroller continues to log data)
		command[0] = "-"
		exit = 1												# Set the exit flag to 1
		powerOff = 1												# Set the powerOff flag to 1

	else:													# Handle invalid input
		command[0] = "-"
		print("> Invalid input. Type help for a list of commands.")						# Notify the user that the command was invalid

print("> Done")												# Notify the user that LoggerShell is exiting
if(powerOff == 1):											# If the powerOff flag is set
	print("PowerOffCLI")
	os.system("poweroff")											# Power off the Raspberry Pi
else:													# Else
	os.system("exit")											# Exit the python script
