
import smbus
import time

bus = smbus.SMBus(1)
def get_ozone():
	data = bus.read_i2c_block_data(0x50, 0x00, 2)
	raw_adc = (data[0] & 0x0F) * 256 + data[1]
	ppm = (1.99 * raw_adc) / 4096.0 + 0.01

	return ppm

def get_altitude():
	bus.write_byte_data(0x60, 0x26, 0xB9)
	bus.write_byte_data(0x60, 0x13, 0x07)
	bus.write_byte_data(0x60, 0x26, 0xB9)
	time.sleep(1)
	data = bus.read_i2c_block_data(0x60, 0x00, 6)

	tHeight = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xf0)) / 16
	altitude = tHeight / 16.0
	
	return altitude

def get_externals():
	bus.write_byte_data(0x60, 0x26, 0xB9)
	bus.write_byte_data(0x60, 0x13, 0x07)
	bus.write_byte_data(0x60, 0x26, 0xB9)
	time.sleep(1)
	data = bus.read_i2c_block_data(0x60, 0x00, 6)

	tHeight = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xf0)) / 16
	temp = ((data[4] * 256) + (data[5] & 0xF0)) /16
	altitude = tHeight / 16.0
	cTemp = temp /16.0
	fTemp = cTemp * 1.8 +32

	bus.write_byte_data(0x60, 0x26, 0x39)
	time.sleep(1)
	data = bus.read_i2c_block_data(0x60, 0x00, 4)
	pres = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
	pressure = (pres / 4.0) / 1000.0


	return altitude, cTemp, pres
