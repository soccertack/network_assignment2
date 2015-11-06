#!/usr/bin/python

#reference
# http://stackoverflow.com/questions/13993514/sending-receiving-file-udp-in-python

import select
import socket
import sys
import struct
import binascii
from common import *

HOST = 'localhost'
PORT = 4118
seg_max_size = 576

file_name="linux-4.3.tar.xz"
file_name="linux.txt"

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
	seq = ord(data[0])
	ack = ord(data[1])

	while data:
		header = make_header(PORT, PORT, seq, ack, 20, 0b00000010, 1, 1, 0)
		data = header + data
		seq += 1
		if s.sendto(data, (HOST, PORT)):
			#print 'keep sending'
			data = f.read(seg_max_size)
	
	# TODO increase ack?

	# Set FIN
	header = make_header (PORT, PORT, seq, ack, 20, 0b00000011, 1, 1, 0)
	data = header
	s.sendto(data, (HOST, PORT))
	print 'Sending FIN'

	# Send FIN bit
	f.close()
	s.close()

if __name__ == '__main__':
	main()
