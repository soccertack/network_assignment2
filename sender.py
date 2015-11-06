#!/usr/bin/python

#reference
# http://stackoverflow.com/questions/13993514/sending-receiving-file-udp-in-python

import select
import socket
import sys
import struct
import binascii

HOST = 'localhost'
PORT = 4118
seg_max_size = 576

file_name="linux-4.3.tar.xz"
#file_name="linux.txt"

def main():
	try:
	    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	except socket.error:
	    print 'Failed to create socket'
	    sys.exit()

	# TODO: exception for opening a file?
	print "file_name" + file_name
	f = open(file_name, "rb")

	data = f.read(seg_max_size)
	values = (PORT, PORT, 1, 1, 20, 0b00000010, 1, 1, 0)
	TCPHeader = struct.Struct('H H I I B B H H H')
	packed_data = TCPHeader.pack(*values)
	print 'Uses :', TCPHeader.size, 'bytes'


	while data:
		data = packed_data + data
		if s.sendto(data, (HOST, PORT)):
			#print 'keep sending'
			data = f.read(seg_max_size)
	
	# Set FIN
	values = (PORT, PORT, 1, 1, 20, 0b00000011, 1, 1, 0)
	TCPHeader = struct.Struct('H H I I B B H H H')
	packed_data = TCPHeader.pack(*values)
	data = packed_data
	s.sendto(data, (HOST, PORT))
	print 'Sending FIN'

	# Send FIN bit
	f.close()
	s.close()

if __name__ == '__main__':
	main()
