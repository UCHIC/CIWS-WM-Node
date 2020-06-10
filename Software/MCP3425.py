# Distributed with a free-will license.
# Use it any way you want, profit or free, provided it fits in the licenses of its associated works.
# MCP3425
# This code is designed to work with the MCP3425_I2CS I2C Mini Module available from ControlEverything.com.
# https://www.controleverything.com/content/Analog-Digital-Converters?sku=MCP3425_I2CADC#tabs-0-product_tabset-2

import smbus

def getVoltage():
	bus = smbus.SMBus(1)
	bus.write_byte(0x68, 0x10)
	data = bus.read_i2c_block_data(0x68, 0x00, 2)
	raw_adc = (data[0] & 0x0F) * 256 + data[1]
	if raw_adc > 2047 :
		raw_adc -= 4095
	return round(raw_adc*.0075,2)
