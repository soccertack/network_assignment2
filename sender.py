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
from crc import *

HOST = 'localhost'
MY_PORT = 20001

REMOTE_IP = 'localhost'
REMOTE_PORT = 20000
seg_max_size = 576
header_length = 5 << 4 	# header size is 32 bit * 5

file_name="ls.svg"
file_name="linux.txt"
file_name="second.coz"
file_name="linux-4.3.tar.xz"

WIN_TIME=1
WIN_SEQ=0
WIN_SIZE=2
WIN_FOFFSET=3

def gobackN():
	print 'gobackN'
	
def send_data(s, data, seq, ack):
	flags = 0
	if not data:
		flags |= FIN_BIT
	checksum = 0
	recv_win = 0
	urg = 0

	header = make_header(MY_PORT, REMOTE_PORT, seq, ack, header_length, flags, recv_win, checksum, urg)
	print data[0:10]
	tmp_data = header + data
	checksum = calc_crc_16(tmp_data);

	header = make_header(MY_PORT, REMOTE_PORT, seq, ack, header_length, flags, recv_win, checksum, urg)
	data = header + data
	if s.sendto(data, (REMOTE_IP, REMOTE_PORT)):
		return 1
	return 0

def wait_for_data (inputs, timeout):
	outputs = []
	readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)
	return readable

def handle_pkt(readable, ack, windows):
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
		if flags & ACK_BIT:
			if recv_ack == (windows[0][WIN_SEQ] + windows[0][WIN_SIZE]):
				windows.remove(windows[0])
		if flags & FIN_BIT:
			fin_ack_recv = 1
			print 'Got a FIN'
	return ack, fin_ack_recv, windows

def make_socket():
	try:
	    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	except socket.error:
	    print 'Failed to create socket'
	    sys.exit()
	s.bind((HOST,MY_PORT))
	return s

def try_to_send(s, data, seq, ack, windows, file_position):
	res = send_data (s, data, seq, ack)
	size = len(data)
	read_new_data = 0
	fin_sent = 0

	if res:
		old_seq = seq
		seq = old_seq + size
		read_new_data = 1
		windows.append((old_seq,datetime.now(), size, file_position))
		if not data:
			fin_sent = 1
	return read_new_data, seq, fin_sent


def main():
	s = make_socket()
	inputs = []
	inputs.append(s)

	# TODO: exception for opening a file?
	print "file_name" + file_name
	f = open(file_name, "rb")
	seq = INIT_SEQ 
	ack = 88888888		# nobody cares

	# initialization
	window_size = 3
	fin_ack_recv = 0
	read_new_data = 1
	timeout = 1
	fin_sent = 0
	exp_ack = 0
	windows = []
	init_crc16()

	while fin_ack_recv == 0:
		file_position = f.tell()
		if read_new_data:
			data = f.read(seg_max_size)
			print 'current fseek', f.tell()
			read_new_data = 0

		if data or (not data and not fin_sent):
			if len(windows) < window_size :
				read_new_data, seq, fin_sent = \
					try_to_send(s, data, seq, ack, windows, file_position)
				continue

		# wait for data
		# TODO: set timeout
		readable = wait_for_data(inputs, timeout)
		if readable:
			ack, fin_ack_recv, windows = handle_pkt(readable, ack, windows)

		if len(windows) == 0:
			continue

		# timeout check
		if (datetime.now() - windows[0][WIN_TIME]) > timedelta(seconds=5):
			read_new_data = 1
			f.seek(windows[0][WIN_FOFFSET], 0)
			seq = windows[0][WIN_SEQ]
			windows = []

	f.close()
	s.close()

if __name__ == '__main__':
	main()
