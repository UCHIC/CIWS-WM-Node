import requests, glob, os, shutil
import disaggregate
import Logger

upload_url = 'http://ciwsdbssandbox.uwrl.usu.edu/data-api'
upload_token_url = 'http://ciwsdbs.uwrl.usu.edu/auth'
client_passcode = 'amVmZl90aGlua3NfaGUnc19jb29s'

# After testing is complete we should use the following variables to upload data to the production server
# upload_token_url = 'http://ciwsdbs.uwrl.usu.edu/auth'
# upload_url = 'http://ciwsdbs.uwrl.usu.edu/data-api'

def processData(toSend):
	directory = '/home/pi/Software/data/'
	for file in os.listdir(directory):
		filename = os.fsdecode(file)
		csv = os.path.join(directory, filename)
		if(toSend is '1' or toSend is '3'):
			file_uploader(csv)
		if(toSend is '2' or toSend is '3'):
			print('Disaggregate transmitted')#file_uploader(disaggregate(csv))
		move(csv, filename)

def move(csv,filename):
	os.rename(csv, os.path.join('/home/pi/Software/sentData/', filename))

def file_uploader(csv):
	try:
		with open(csv, 'rb') as data_file:
			files = [('data_file[]', data_file), ]
			upload_token = requests.post(upload_token_url, data={'token': client_passcode, 'filenames': csv})
			upload_response = requests.post(upload_url, headers={'Authorization': 'Bearer {upload_token.text}'}, files=files)
			rsp = upload_response.text
			print (rsp)
	except:
		print('Failed to transmit.')
