import WEUDseven
def crunchData(file):  # pass in file name to be processed
	try:
		return [WEUDseven.WEUD(file)]           #Return list of file names for output data
	except:
		return []
