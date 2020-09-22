import Logger
import sys
import os

########################################################
#                 LoggerReportSwap.py                  #
########################################################
#                                                      #
# This code exchanges report data with the             #
# microcontroller. The report data includes date,      #
# time, and other such information.                    #
#                                                      #
########################################################

## Report format:
#
#  Year
#  Month
#  Day
#  Hour
#  Minute
#  Second
#  Pulses in the last period
#  Total pulses (byte 0)
#  Total pulses (byte 1)
#  Total pulses (byte 2)
#  Logging flag (y/n)
#  Time of period (i.e. sample rate)

# Make sure every report field is specified in arguments

if len(sys.argv) != 13:
	print("Bad Arguments")
	sys.exit(os.EX_USAGE)

# Compile report fields into a single list

report = [int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7]), int(sys.argv[8]), int(sys.argv[9]), int(sys.argv[10]), int(sys.argv[11]), int(sys.argv[12])]

# Swap report data with the microcontroller

Logger.init()
loggerReport = Logger.reportSwap(report)

# Print the received report

for i in range(0,12):
	print(loggerReport[i], " ")
