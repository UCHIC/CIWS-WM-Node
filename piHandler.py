import requests, glob, os, shutil, ast

import WEUDseven

upload_url = 'http://ciwsdbssandbox.uwrl.usu.edu/data-api'
upload_token_url = 'http://ciwsdbs.uwrl.usu.edu/auth'
client_passcode = 'amVmZl90aGlua3NfaGUnc19jb29s'


def processData():
	files_grabbed = glob.glob('/home/pi/Software/data/*.csv')
	toSend = readConfig('Transmission')
	toStore = readConfig('Storage')
	print('files grabber:', files_grabbed)
	for filenames in files_grabbed:
		if toSend in ['2','3'] or toStore is not '1':
			for disagcsv in dataAnalysis(filenames):
				print(disagcsv)
				if disagcsv:
					if toSend in ['2','3']:
						if send(disagcsv.split('/')[-1]):
							if toStore is not '1':
								shutil.move(disagcsv, '/home/pi/Software/savedData/' + disagcsv.split('/')[-1])
							else:
								os.remove(disagcsv)
					else:
						if toStore is not '1':
							shutil.move(disagcsv, '/home/pi/Software/savedData/' + disagcsv.split('/')[-1])
						else:
							os.remove(disagcsv)
		if toSend in ['1','3']:
			if send(filenames.split('/')[-1]):
				if toStore is not '2':
					shutil.move(filenames, '/home/pi/Software/savedData/' + filenames.split('/')[-1])
				else:
					os.remove(filenames)
		else:
			if toStore is not '2':
				shutil.move(filenames, '/home/pi/Software/savedData/' + filenames.split('/')[-1])
			else:
				os.remove(filenames)

def send(file):
	success = True
	try:
		os.chdir('/home/pi/Software/data/')
		with open(file, 'rb') as data_file:
			files = [('data_file[]', data_file), ]
			upload_token = requests.post(upload_token_url, data={'token': client_passcode, 'filenames': file})
			upload_response = requests.post(upload_url, headers={'Authorization': f'Bearer {upload_token.text}'},files=files).text
			print('>', ast.literal_eval(upload_response)[file])
			if 'successfully' in upload_response:
				pass
			else:
				success = False
	except:
		print('Failed to send', file)
		success = False
	finally:
		os.chdir('/home/pi/Software/')
		return success


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
	except:
		f.close()
		return "Error Reading " + key


def dataAnalysis(file):  # pass in file name to be processed
	try:
		return [WEUDseven.WEUD(file)]           #Return list of file names for output data
	except Exception as e:
		print(str(e))
		return []