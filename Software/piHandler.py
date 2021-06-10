import requests, glob, os, shutil, ast

###
#Parameters for transmission to server
#If left blank transmission will be ignored
###
upload_url = ''
upload_token_url = ''
client_passcode = ''

###
#Handles the dissaggregation, transmission, and storage of data
###
def processData():
	files_grabbed = glob.glob('/home/pi/Software/data/*.csv')	#grabs all csv files fron the data directory(data from eeprom is stored in data directory)
	toSend = readConfig('Transmission')	#Read setting for what data to transmit
	toStore = readConfig('Storage')		#Read setting for what data to store on pi
	for filenames in files_grabbed:		#For each raw data file
		if toSend in ['2','3'] or toStore is not '1':	#Checks if disaggregation is necessary based on transmissiona and storage settings
			for disagcsv in dataAnalysis(filenames):	#For every file returned by computations done on the raw data
				if disagcsv:				#If string is valid
					if toSend in ['2','3']:		#If transmission setting calls for transmitting computational data
						send(disagcsv.split('/')[-1])	#Send computational data to the server
					if toStore is not '1':		#If storage setting calls for saving computional data on the pi
						shutil.move(disagcsv, '/home/pi/Software/savedData/' + disagcsv.split('/')[-1])	#Move file to savedData directory
					else:				#Else
						os.remove(disagcsv)	#Delete file
		if toSend in ['1','3']:					#If raw data is to be sent to server
			send(filenames.split('/')[-1])			#Send raw data
		if toStore is not '2':					#If raw data is to be saved on the pi
			shutil.move(filenames, '/home/pi/Software/savedData/' + filenames.split('/')[-1])	#Move file to savedData directory
		else:							#Else
			os.remove(filenames)				#Delete file

###
#For sending files to a server
#Accepts a file name and sends that file to a server using the parameters above
#Called in the processData() function
###
def send(file):
	try:
		os.chdir('/home/pi/Software/data/')	#Change working directory to data
		with open(file, 'rb') as data_file:
			files = [('data_file[]', data_file), ]
			upload_token = requests.post(upload_token_url, data={'token': client_passcode, 'filenames': file})
			upload_response = requests.post(upload_url, headers={'Authorization': f'Bearer {upload_token.text}'},files=files).text
			print('>', ast.literal_eval(upload_response)[file])
	except:
		print('Failed to send', file)	#If fail print file name
	finally:
		os.chdir('/home/pi/Software/')	#Change working directory to Software

###
#Writes configurating settings to the configure.txt file
#Accepts a value and the key to write too
#Returns value as read fron cofiguration file
###
def writeConfig(key, value):
	f = open('/home/pi/Software/configure.txt','r+')	#Opens configure.txt in read only
	try:
		dict = ast.literal_eval(f.read())		#Converts file contents to a discionary
	except:
		dict = {'ID': '', 'Site': '', 'Period': '', 'meterResolution': '', 'Transmission': '3', 'Storage': '3'}	#If fail create dictionary 
	finally:
		f.close()	#Close file
	dict[key] = value	#Write new value to dictionary
	f = open('configure.txt', 'w')	#Open configure.txt in write
	f.write(str(dict))		#Convert changed dictionary to string and write to file
	f.close()			#Close file
	return readConfig(key)		#Return key as read from configuration file

###
#Reads from configuration file
#Accepts a key
#Returns value for key
###
def readConfig(key):
	try:
		f = open('/home/pi/Software/configure.txt', 'r+')	#Open configure.txt file
		dict = ast.literal_eval(f.read())			#Convert string to dictionary
		f.close()						#Close file
		return dict[key]					#Return value
	except:								#If exception
		f.close()						#Close file
		return "Error Reading " + key				#Print what key couldnt be read

###
#Function to handle the analysis of raw data
#INSTRUCTIONS
#1. Import your analysis code into this file
#2. Add the function from your code into the return array within the try block
#3. Add file variable as a parameter to your function
#4. NOTE: Your function must return a file as its output with a different name to the one being passed to it
#EXAMPLE: If I had a file named analyze and a function within that file named mean id put "import mean from analyze" at the top of this file
#		Then then the dataAlalysis code would look like:
#def dataAnalysis(file):
#	try:
#		return [mean(file)]
#	except Exception as e:
#		print(str(e))
#		return []
#
#Multiple analyses can be performed by seperating the functions with a comma in the return array
###

def dataAnalysis(file):  # pass in file name to be processed
	try:
		return []           #Return list of file names for output data
	except Exception as e:
		print(str(e))
		return []
