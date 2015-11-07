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
file_name="ls.svg"
file_name="linux.txt"
file_name="second.coz"

def send_data(s, data, seq, ack):
	flag = 0b00000010
	if not data:
		flag |= FIN_BIT
	header = make_header(PORT, PORT, seq, ack, 20, flag, 1, 1, 0)
	data = header + data
	if s.sendto(data, (HOST, PORT)):
		return 1
	return 0

def wait_for_data (inputs, timeout):
	outputs = []
	readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)
	return readable

def handle_pkt(readable, cur_window, ack):
	fin_ack_recv = 0
	for item in readable:
		d = item.recvfrom(1024)
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
			ack = recv_seq +1
		if flags & FIN_BIT:
			fin_ack_recv = 1
		cur_window += 1
	return cur_window, ack, fin_ack_recv


def main():
	try:
	    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	except socket.error:
	    print 'Failed to create socket'
	    sys.exit()

	inputs = []
	inputs.append(s)
	# TODO: exception for opening a file?
	print "file_name" + file_name
	f = open(file_name, "rb")
	seq = 7000
	ack = 88888888		# nobody cares

	cur_window = 3

	fin_ack_recv = 0
	read_new_data = 1
	timeout = 1
	fin_sent = 0
	while fin_ack_recv == 0:
		if read_new_data:
			data = f.read(seg_max_size)
			read_new_data = 0

		if data or (not data and not fin_sent):
			if cur_window != 0:
				res = send_data (s, data, seq, ack)
				if res:
					seq += sys.getsizeof(data)
					cur_window -= 1
					read_new_data = 1
					print 'send data'
					if not data:
						fin_sent = 1
				continue
		print 'wait for data'
		readable = wait_for_data(inputs, timeout)
		if readable:
			cur_window, ack, fin_ack_recv = handle_pkt(readable, cur_window, ack)
		else:
			print 'gobackn'

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
