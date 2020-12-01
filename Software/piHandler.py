import ast

import requests, glob, os, shutil, arduinoHandler


upload_url = ''
upload_token_url = ''
client_passcode = ''


def processData():
	files_grabbed = glob.glob('/home/pi/Software/data/*.csv')
	toSend = readConfig('Transmission')
	toStore = readConfig('Storage')
	for filenames in files_grabbed:
		if toSend in ['2','3'] or toStore is not '1':
			for disagcsv in dataAnalysis(filenames):
				if disagcsv:
					if toSend in ['2','3']:
						send(disagcsv.split('/')[-1])
					if toStore is not '1':
						shutil.move(disagcsv, '/home/pi/Software/savedData/' + disagcsv.split('/')[-1])
					else:
						os.remove(disagcsv)
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
		dict = {'ID': '', 'Site': '', 'Period': '', 'meterResolution': '', 'Transmission': '', 'Storage': ''}
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
		f.close()
	except:
		return "Error Reading " + key


def dataAnalysis(file):  # pass in file name to be processed
	try:
		return []           #Return list of file names for output data
	except:
		return []
