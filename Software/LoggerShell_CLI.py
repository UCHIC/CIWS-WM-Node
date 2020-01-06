import subprocess
import os
import Logger

exit = 0
powerOff = 0
command = ["-", "-", "-"]
Logger.init()

print " "
print "======================== LoggerShell ========================"
print "|                                                           |"
print "| Welcome to the LoggerShell Command-Line Interface         |"
print "| Type help for a list of commands                          |"
print "|                                                           |"
print "============================================================="
print " "

while(exit == 0):
	print "> "
	userInput = raw_input("> ")

	if(userInput == "start-logging"):
		command[0] = "python LoggerReportSwap.py 255 255 255 255 255 255 255 255 255 255 255"
		command[1] = "python LoggerReportSwap.py 255 255 255 255 255 255 255 255 255 255 1"
		process = subprocess.Popen(command[0], stdout=subprocess.PIPE, shell=True)
		(output, err) = process.communicate()
		p_status = process.wait()
		outputList = output.split()
		process = subprocess.Popen(command[0], stdout=subprocess.PIPE, shell=True)
		(output, err) = process.communicate()
		p_status = process.wait()
		outputList = output.split()
		if(int(outputList[10]) == 1):
			print "> Device already logging"
		else:
			process = subprocess.Popen(command[1], stdout=subprocess.PIPE, shell=True)
			(output, err) = process.communicate()
			p_status = process.wait()
			process = subprocess.Popen(command[0], stdout=subprocess.PIPE, shell=True)
			(output, err) = process.communicate()
			p_status = process.wait()
			outputList = output.split()
			if(int(outputList[10]) == 1):
				print "> Logging started successfully"
			else:
				print "> Logging was not started, logging field == ", outputList[10]
	elif(userInput == "stop-logging"):
		command[0] = "python LoggerReportSwap.py 255 255 255 255 255 255 255 255 255 255 255"
		command[1] = "python LoggerReportSwap.py 255 255 255 255 255 255 255 255 255 255 0"
		command[2] = "python LoggerReadRom.py"
		process = subprocess.Popen(command[0], stdout=subprocess.PIPE, shell=True)
		(output, err) = process.communicate()
		p_status = process.wait()
		outputList = output.split()
		if(int(outputList[10]) == 0):
			print "> Device is not logging"
		else:
			print "> Setting stop bit..."
			process = subprocess.Popen(command[1], stdout=subprocess.PIPE, shell=True)
			(output, err) = process.communicate()
			p_status = process.wait()
			print "> Reading EEPROM..."
			process = subprocess.Popen(command[2], stdout=subprocess.PIPE, shell=True)
			(output, err) = process.communicate()
			p_status = process.wait()
			print "> Checking stop bit..."
			process = subprocess.Popen(command[0], stdout=subprocess.PIPE, shell=True)
			(output, err) = process.communicate()
			p_status = process.wait()
			outputList = output.split()
			if(int(outputList[10]) == 0):
				print "> Logging stopped successfully"
			else:
				print "> Logging was not stopped, logging field == ", outputList[10]
	elif(userInput == "date-time"):
		command[0] = "python LoggerReportSwap.py 255 255 255 255 255 255 255 255 255 255 255"
		process = subprocess.Popen(command[0], stdout=subprocess.PIPE, shell=True)
		(output, err) = process.communicate()
		p_status = process.wait()
		outputList = output.split()
		Date = outputList[1] + "/" + outputList[2] + "/" + "20" + outputList[0]
		Time = outputList[3] + ":" + outputList[4] + ":" + outputList[5]
		print ">", Date
		print ">", Time
	elif(userInput == "update-date-time"):
		newMonth = raw_input("> Month: ")
		newDay = raw_input("> Day: ")
		newYear = raw_input("> Year: ")
		newHour = raw_input("> Hour: ")
		newMinute = raw_input("> Minute: ")
		newSecond = raw_input("> Second: ")
		space = " "
		command[0] = "python LoggerReportSwap.py " + newYear + space + newMonth + space + newDay + space + newHour + space + newMinute + space + newSecond + " 255 255 255 255 255"
		command[1] = "python LoggerReportSwap.py 255 255 255 255 255 255 255 255 255 255 255"
		process = subprocess.Popen(command[0], stdout=subprocess.PIPE, shell=True)
		(output, err) = process.communicate()
		p_status = process.wait()
		process = subprocess.Popen(command[1], stdout=subprocess.PIPE, shell=True)
		(output, err) = process.communicate()
		p_status = process.wait()
		outputList = output.split()
		Date = outputList[1] + "/" + outputList[2] + "/" + "20" + outputList[0]
		Time = outputList[3] + ":" + outputList[4] + ":" + outputList[5]
		print ">", Date
		print ">", Time
	elif(userInput == "set-id"):
		newID = raw_input("> New ID: ")
		Logger.setID(newID)
	elif(userInput == "get-id"):
		ID = Logger.getID()
		print "> Datalogger ID:", ID
	elif(userInput == "set-site"):
		newSite = raw_input("> New Site: ")
		Logger.setSiteNumber(newSite)
	elif(userInput == "get-site"):
		site = Logger.getSiteNumber()
		print "> Datalogger Site:", site
	elif(userInput == "set-meter"):
		newMeterRez = raw_input("> New Meter Resolution: ")
		Logger.setMeterResolution(newMeterRez)
	elif(userInput == "get-meter"):
		meterRez = Logger.getMeterResolution()
		print "> Meter Resolution:", meterRez
	elif(userInput == "water-flow"):
		command[0] = "python LoggerReportSwap.py 255 255 255 255 255 255 255 255 255 255 255"
		process = subprocess.Popen(command[0], stdout=subprocess.PIPE, shell=True)
		(output, err) = process.communicate()
		p_status = process.wait()
		outputList = output.split()
		pulseCount = int(outputList[6])
		totalCount = (int(outputList[7]) << 16) + (int(outputList[8]) << 8) + int(outputList[9])
		waterFlow = pulseCount * float(Logger.getMeterResolution()) * 60.0 / 4.0
		totalWaterFlow = float(totalCount) * float(Logger.getMeterResolution())
		print "> Pulses in last period:", pulseCount
		print "> Estimated water flow:", waterFlow, "GPM"
		print "> Total pulses counted:", totalCount
		print "> Total water flow:", totalWaterFlow, "Gal"
	elif(userInput == "help"):
		command[0] = "-"
		print "> LoggerShell is a shell interface for all of the"
		print "> functionality between the Raspberry Pi and the"
		print "> datalogging microcontroller. The following is a list"
		print "> of commands:"
		print ">"
		print "> date-time        // Displays the current date/time"
		print "> update-date-time // Updates the current date/time"
		print "> exit             // Exit from LoggerShell"
		print "> exit-poweroff    // Exit from LoggerShell and power off"
		print "> start-logging    // Begin logging data"
		print "> stop-logging     // Stop logging data"
		print "> set-id           // Set a new datalogger ID number"
		print "> get-id           // Read and display the datalogger ID number"
		print "> set-site         // Set a new datalogger site number"
		print "> get-site         // Read and display the datalogger site number"
		print "> set-meter        // Set a meter resolution for the datalogger"
		print "> get-meter        // Read and display the meter resolution for the datalogger"
		print "> water-flow       // Display water flow data for the previous sample"
	elif(userInput == "exit"):
		command[0] = "-"
		print "> To restart LoggerShell, execute the following command: sudo python LoggerShell_CLI.py"
		exit = 1
	elif(userInput == "exit-poweroff"):
		command[0] = "-"
		exit = 1
		powerOff = 1
	else:
		command[0] = "-"
		print "> Invalid input. Type help for a list of commands."

print "> Done"
if(powerOff == 1):
	os.system("poweroff")
else:
	os.system("exit")
