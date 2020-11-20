import requests, glob, os, shutil
from crunchData import crunchData

upload_url = ''        #upload url for uploading data to server
upload_token_url = ''  #token for uploading data to server
client_passcode = ''   #passcode fro uploading data to server


def processData(toSend, toStore):
	os.chdir('/home/pi/Software/data/')
	cd = os.getcwd() + "/"
	out = '/home/pi/Software/savedData/'
	if not os.path.exists(out):
		os.makedirs(out)
	files_grabbed = []                                                         #create list for files
	for files in ('*.CSV', '*.csv'):                                           #grab all files with csv extension(files created from logging)
		files_grabbed.extend(glob.glob(files))
	for filenames in files_grabbed:                                            #for all files grabbed
		if toSend in ['2','3'] or toStore is not '1':                      #if disaggregated data will be sent or saved disaggregate data
			for disagcsv in crunchData(filenames):                     #for each file name returned from crunchdata(crunch data returns file names for however many analysis methods it contains)
				if disagcsv:
					if toSend in ['2','3']:                            #do send settings allow disaggregated data to be sent
						send(disagcsv)
					if toStore is not '1':                             #do save settings allow disaggregated data to be saved
						shutil.move(cd + disagcsv, out + disagcsv)
					else:                                              #if disaggregated data isnt supposed to be saved then remove it
						os.remove(cd + disagcsv)
		if toSend in ['1','3']:                                            #do send settings allow raw data to be sent
			send(filenames)
		if toStore is not '2':                                             #do save settings allow raw data to be saved
			shutil.move(cd + filenames, out + filenames)
		else:
			os.remove(cd + filenames)                                  #if raw data isnt supposed to be saved then remove it
			
def send(file):   #function for sending data to server
	try:
		with open(file, 'rb') as data_file:
			files = [('data_file[]', data_file), ]
			upload_token = requests.post(upload_token_url, data={'token': client_passcode, 'filenames': file})
			upload_response = requests.post(upload_url, headers={'Authorization': f'Bearer {upload_token.text}'},files=files)
			print(upload_response.text)
	except:
		print('Failed to send', file)
