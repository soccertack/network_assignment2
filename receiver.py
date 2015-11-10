#!/usr/bin/python

#reference
# http://www.binarytides.com/programming-udp-sockets-in-python/

import select
import socket
import sys
from datetime import datetime
from threading import Thread
import struct
import binascii
from common import *
from crc import *

HOST = ''
my_port = 20000
sender_ip = ''
sender_port = 0
 
file_name = "received.txt"

def handle_input(argv):
	argc = len(argv)
	if argc != 6:
		print 'Usage: ./receiver.py filename listening_port sender_IP sender_port log_file  '
		sys.exit()
	global file_name, my_port, log_file, sender_ip, sender_port
	file_name = argv[1]
	my_port	= int(argv[2])
	sender_ip = argv[3]
	sender_port = int(argv[4])
	log_file = argv[5]

def main():
	handle_input(sys.argv)

	seq = INIT_SEQ 
	try :
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		print 'Socket created'
	except socket.error, msg :
		print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
		sys.exit()
	 
	 
	init_crc16()
	# Bind socket to local host and port
	try:
		s.bind((HOST, my_port))
	except socket.error , msg:
		print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
		sys.exit()
		 
	print 'Socket bind complete'

	TCPHeader = struct.Struct('H H I I B B H H H')
 
	f = open(file_name, "wb")
	if log_file == "stdout":
		f_log = sys.stdout
	else:
		f_log = open(log_file, "w")

	exp_seq = INIT_SEQ
	#now keep talking with the client
	while 1:
		# receive data from client (data, addr)
		d = s.recvfrom(1024)
		data = d[0]
		if not data: 
			break
		 
		header = data[:20]
	   	payload = data[20:]
		(src, dst, recv_seq, recv_ack, header,recv_flags, recv_win, checksum, urg)\
			= TCPHeader.unpack(header)

		write_log (src, dst, recv_seq, recv_ack, recv_flags, f_log)

		tmp_header = make_header(src, dst, recv_seq, recv_ack, header, recv_flags, recv_win, 0, urg)
		checksum_calc = calc_crc_16(tmp_header+payload)
		if checksum_calc != checksum:
			continue	# Wrong packet
	
		if recv_seq != exp_seq:
			continue
		exp_seq += len(payload)
		ack = recv_seq + len(payload) 
		flags = ACK_BIT
		if recv_flags & FIN_BIT:
			flags |= FIN_BIT
		pkt = make_header(my_port, src, seq, ack, 20, flags, 0, 0, 0)
		s.sendto(pkt, (sender_ip, sender_port))
		write_log (my_port, src, seq, ack, flags, f_log)

		f.write(data[20:]);

		if recv_flags & FIN_BIT:
			break
	s.close()
	f.close()
	f_log.close()

if __name__ == '__main__':
	main()
