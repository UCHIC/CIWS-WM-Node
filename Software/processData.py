import requests, glob, os, shutil
from crunchData import crunchData

upload_url = ''
upload_token_url = ''
client_passcode = ''


def processData(toSend, toStore):
	os.chdir('/home/pi/Software/data/')
	cd = os.getcwd() + "/"
	out = '/home/pi/Software/savedData/'
	if not os.path.exists(out):
		os.makedirs(out)
	types = ('*.CSV', '*.csv')
	files_grabbed = []
	for files in types:
		files_grabbed.extend(glob.glob(files))
	for filenames in files_grabbed:
		if toSend in ['2','3'] or toStore is not '1':
			for disagcsv in crunchData(filenames):
				if toSend in ['2','3']:
					with open(disagcsv, 'rb') as data_file:
						files = [('data_file[]', data_file), ]
						upload_token = requests.post(upload_token_url,data={'token': client_passcode, 'filenames': disagcsv})
						upload_response = requests.post(upload_url,headers={'Authorization': f'Bearer {upload_token.text}'},files=files)
						print(upload_response.text)

				if toStore is not '1':
					shutil.move(cd + disagcsv, out + disagcsv)
				else:
					os.remove(cd + disagcsv)
		if toSend in ['1','3']:
			with open(filenames, 'rb') as data_file:
				files = [('data_file[]', data_file), ]
				upload_token = requests.post(upload_token_url, data={'token': client_passcode, 'filenames': filenames})
				upload_response = requests.post(upload_url, headers={'Authorization': f'Bearer {upload_token.text}'},files=files)
				print(upload_response.text)
		if toStore is not '2':
			shutil.move(cd + filenames, out + filenames)
		else:
			os.remove(cd + filenames)
