#!/usr/bin/python

#reference
# http://stackoverflow.com/questions/13993514/sending-receiving-file-udp-in-python

import select
import socket
import sys
import struct
import binascii
from common import *
from datetime import datetime
from datetime import timedelta

HOST = 'localhost'
PORT = 4118
seg_max_size = 576

file_name="linux-4.3.tar.xz"
file_name="ls.svg"
file_name="linux.txt"
file_name="second.coz"

def gobackN():
	print 'gobackN'
	
def send_data(s, data, seq, ack):
	flag = 0b00000010
	if not data:
		flag |= FIN_BIT
	header = make_header(PORT, PORT, seq, ack, 20, flag, 1, 1, 0)
	print data[0:10]
	data = header + data
	if s.sendto(data, (HOST, PORT)):
		return 1
	return 0

def wait_for_data (inputs, timeout):
	outputs = []
	readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)
	return readable

def handle_pkt(readable, ack):
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
			# TODO: check ack number
			ack = recv_seq +1
			# TODO: remove matching item from the window
		if flags & FIN_BIT:
			fin_ack_recv = 1
	return ack, fin_ack_recv


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

	window_size = 3

	fin_ack_recv = 0
	read_new_data = 1
	timeout = 1
	fin_sent = 0
	exp_ack = 0
	# Need to manage list of N
	windows = []
	while fin_ack_recv == 0:
		file_position = f.tell()
		if read_new_data:
			data = f.read(seg_max_size)
			print 'current fseek', f.tell()
			read_new_data = 0

		if data or (not data and not fin_sent):
			if len(windows) < window_size :
				res = send_data (s, data, seq, ack)
				size = len(data)
				print size
				if res:
					old_seq = seq
					seq = old_seq + size
					read_new_data = 1
					windows.append((old_seq,datetime.now(), size, file_position))
					if not data:
						fin_sent = 1
				continue

		# wait for data
		readable = wait_for_data(inputs, timeout)
		if readable:
			ack, fin_ack_recv = handle_pkt(readable, ack)
		if (datetime.now() - windows[0][1]) > timedelta(seconds=5):
			read_new_data = 1
			total_size = 0
			for pkt in windows:
				total_size += pkt[2]
			print 'total size', total_size
			f.seek(windows[0][3], 0)
			seq = windows[0][0]
			windows = []

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
