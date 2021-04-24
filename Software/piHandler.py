import requests, glob, os, shutil, ast

upload_url = ''
upload_token_url = ''
client_passcode = ''


# This function reads files from the data directory and processes them.
# This includes dissagregation/analysis, transmission to remote server, and storage of data on the device.

def processData():
	files_grabbed = glob.glob('/home/pi/Software/data/*.csv')  # Grab files from data directory
	toSend = readConfig('Transmission')  # Read transmission setting((3)send all data/(2)just disaggregated data/(1)just raw data)
	toStore = readConfig('Storage')  # Read Storage setting((3)store all data/(2)just disaggregated data/(1)just raw data)
	print('files grabber:', files_grabbed)
	for filenames in files_grabbed:  # For each file in the data directory
		if toSend in ['2','3'] or toStore is not '1': # Check if dissagregated data will be trasmitted or stored(If not then no reason to disaggregated)
			for disagcsv in dataAnalysis(filenames):  # For each file returned by data analysis
				print(disagcsv)
				if disagcsv:  # If file exists
					if toSend in ['2','3']:  # If file is supposed to be sent to server
						send(disagcsv.split('/')[-1])  # Send to server
					if toStore is not '1':  # If file is supposed to be saved on device
						shutil.move(disagcsv, '/home/pi/Software/savedData/' + disagcsv.split('/')[-1])  # Save on device
					else:
						os.remove(disagcsv)  # If file is not supposed to be saved then delete it
		if toSend in ['1','3']:
			send(filenames.split('/')[-1])
		if toStore is not '2':
			shutil.move(filenames, '/home/pi/Software/savedData/' + filenames.split('/')[-1])
		else:
			os.remove(filenames)

def send(file):
	try:
		os.chdir('/home/pi/Software/data/')
		with open(file, 'rb') as data_file:
			files = [('data_file[]', data_file), ]
			upload_token = requests.post(upload_token_url, data={'token': client_passcode, 'filenames': file})
			upload_response = requests.post(upload_url, headers={'Authorization': f'Bearer {upload_token.text}'},files=files).text
			print('>', ast.literal_eval(upload_response)[file])
	except:
		print('Failed to send', file)
	finally:
		os.chdir('/home/pi/Software/')


def writeConfig(key, value):
	f = open('/home/pi/Software/configure.txt','r+')
	try:
		dict = ast.literal_eval(f.read())
	except:
		dict = {'ID': '', 'Site': '', 'Period': '', 'meterResolution': '', 'Transmission': '1', 'Storage': '1'}
	finally:
		f.close()
	dict[key] = value
	f = open('configure.txt', 'w')
	f.write(str(dict))
	f.close()
	return readConfig(key)


def readConfig(key):
	try:
		f = open('/home/pi/Software/configure.txt', 'r+')
		dict = ast.literal_eval(f.read())
		f.close()
		return dict[key]
	except:
		f.close()
		return "Error Reading " + key


def dataAnalysis(file):  # pass in file name to be processed
	try:
		return []           #Return list of file names for output data
	except Exception as e:
		print(str(e))
		return []
