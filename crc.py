from array import array
import binascii
import struct

# http://www.lammertbies.nl/comm/info/crc-calculation.html

P_16=0xA001

crc_tab16 = array('H')
def init_crc16():
	for i in range(0,256):
		crc = 0
		c = i
		for j in range(0, 8):
			if (crc ^ c) & 0x0001:
				crc = (crc>>1) ^ P_16
			else:
				crc = crc >> 1
			c = c >> 1
		crc_tab16.append(crc)
				
def update_crc_16 (crc, c):
        short_c = 0x00ff &  c;
	tmp =  crc ^ short_c;
	crc = (crc >> 8) ^ crc_tab16[ tmp & 0xff ];
	return crc

def calc_crc_16 (data):
	size = len(data)
	crc = 0

	for i in range(0,size):
		up = struct.unpack('B', data[i])
		crc = update_crc_16(crc, up[0])

	return crc
