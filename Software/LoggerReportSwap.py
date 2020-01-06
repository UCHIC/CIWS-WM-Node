import Logger
import sys
import os

if len(sys.argv) != 12:
	print("Bad Arguments")
	sys.exit(os.EX_USAGE)

report = [int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7]), int(sys.argv[8]), int(sys.argv[9]), int(sys.argv[10]), int(sys.argv[11])]

Logger.init()
loggerReport = Logger.reportSwap(report)

for i in range(0,11):
	print loggerReport[i], " ",
