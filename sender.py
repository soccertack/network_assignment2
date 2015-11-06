#!/usr/bin/python

#reference
# http://stackoverflow.com/questions/13993514/sending-receiving-file-udp-in-python

import select
import socket
import sys

HOST = 'localhost'
PORT = 4118
seg_max_size = 576

file_name="linux-4.3.tar.xz"
file_name="linux.txt"

if __name__ == '__main__':
	try:
	    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	except socket.error:
	    print 'Failed to create socket'
	    sys.exit()

	# TODO: exception for opening a file?
	print "file_name" + file_name
	f = open(file_name, "rb")

	data = f.read(seg_max_size)
	while data:
		if s.sendto(data, (HOST, PORT)):
			print 'keep sending'
			data = f.read(seg_max_size)
	f.close()
	s.close()

