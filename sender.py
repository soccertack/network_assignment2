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
file_name="second.coz"
file_name="ls.svg"

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
	print 'init seq: ', seq
	ack = ord(data[1])
	print 'init ack: ', ack

	cur_window = 1
	while data:
		if cur_window == 0:
			d = s.recvfrom(1024)
			data = d[0]
			addr = d[1]

			if not data:
				break;
			header = data[:20]
			payload = data[20:]
			(src, dst, recv_seq, recv_ack, header,flags, recv_win, checksum, urg)= TCPHeader.unpack(header)
			print src, dst, recv_seq, recv_ack, header,flags, recv_win, checksum, urg
			# TODO: checksum 
			'''
			if checksum(payload) != checksum:
			continue
			'''
			if flags & ACK_BIT:
				seq = recv_ack
				ack = recv_seq +1
			cur_window += 1

		else:
			header = make_header(PORT, PORT, seq, ack, 20, 0b00000010, 1, 1, 0)
			data = header + data
			if s.sendto(data, (HOST, PORT)):
				#print 'keep sending'
				data = f.read(seg_max_size)
				cur_window -= 1
	
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
