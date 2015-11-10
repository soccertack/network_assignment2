#!/usr/bin/python

#reference
# http://stackoverflow.com/questions/13993514/sending-receiving-file-udp-in-python

import select
import socket
import sys
import struct
import binascii
from common import *
from datetime import timedelta
from crc import *

HOST = ''
my_port = 20001

remote_ip = 'localhost'
remote_port = 20000
seg_max_size = 576
header_length = 5 << 4 	# header size is 32 bit * 5
file_name=""

window_size = 0

WIN_TIME=1
WIN_SEQ=0
WIN_SIZE=2
WIN_FOFFSET=3

total_bytes_sent = 0
total_seg_sent = 0
total_retrans = 0

def send_data(s, data, seq, ack, f_log):
	flags = 0
	if not data:
		flags |= FIN_BIT
	else:
		global total_bytes_sent, total_seg_sent
		total_bytes_sent += len(data)
		total_seg_sent += 1

	checksum = 0
	recv_win = 0
	urg = 0

	header = make_header(my_port, remote_port, seq, ack, header_length, flags, recv_win, checksum, urg)
	tmp_data = header + data
	checksum = calc_crc_16(tmp_data);

	header = make_header(my_port, remote_port, seq, ack, header_length, flags, recv_win, checksum, urg)
	data = header + data
	write_log(my_port, remote_port, seq, ack, flags, f_log)
	if s.sendto(data, (remote_ip, remote_port)):
		return 1
	return 0

def wait_for_data (inputs, timeout):
	outputs = []
	readable, writable, exceptional = select.select(inputs, outputs, inputs, timeout)
	return readable

def handle_pkt(readable, ack, windows, f_log):
	fin_ack_recv = 0
	if len(windows) == 0:
		return ack, fin_ack_recv, windows

	for item in readable:
		d = item.recvfrom(1024)
		data = d[0]
		addr = d[1]

		if not data:
			break;

		header = data[:20]
		payload = data[20:]
		(src, dst, recv_seq, recv_ack, header,flags, recv_win, checksum, urg)= TCPHeader.unpack(header)

		rtt = (datetime.now()-windows[0][WIN_TIME]).total_seconds()*1000
		write_log(src, dst, recv_seq, recv_ack, flags, f_log, rtt)
		if flags & ACK_BIT:
			if recv_ack == (windows[0][WIN_SEQ] + windows[0][WIN_SIZE]):
				windows.remove(windows[0])
		if flags & FIN_BIT:
			fin_ack_recv = 1
		ack = recv_seq + len(payload) + 1
	return ack, fin_ack_recv, windows

def make_socket():
	try:
	    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	except socket.error:
	    print 'Failed to create socket'
	    sys.exit()
	s.bind((HOST,my_port))
	return s

def try_to_send(s, data, seq, ack, windows, file_position, f_log):
	res = send_data (s, data, seq, ack, f_log)
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

def handle_input(argv):

	argc = len(argv)
	if argc != 6 and argc !=7:
		print 'Usage: ./sender.py filename remote_IP remote_port  \
			ack_port_num log_filename window_size'
		sys.exit()
	global file_name, remote_ip, remote_port, my_port, log_file, window_size
	file_name = argv[1]
	remote_ip = argv[2]
	remote_port = int(argv[3])
	my_port	= int(argv[4])
	log_file = argv[5]
	window_size = 1
	if argc == 7:
		window_size = int(argv[6])

def main():

	handle_input(sys.argv)
	s = make_socket()
	inputs = []
	inputs.append(s)

	try:
		f = open(file_name, "rb")
	except (OSError, IOError) as e:
		print 'file open error'
		sys.exit()
	if log_file == "stdout":
		f_log = sys.stdout
	else:
		f_log = open(log_file, "w")

	seq = INIT_SEQ 
	ack = INIT_SEQ # nobody cares

	# initialization
	fin_ack_recv = 0
	read_new_data = 1
	timeout = 0.3
	fin_sent = 0
	exp_ack = 0
	windows = []
	init_crc16()

	while fin_ack_recv == 0:
		file_position = f.tell()
		if read_new_data:
			data = f.read(seg_max_size)
			read_new_data = 0

		if data or (not data and not fin_sent):
			if len(windows) < window_size :
				read_new_data, seq, fin_sent = \
					try_to_send(s, data, seq, ack, windows, file_position, f_log)
				continue

		# wait for data
		readable = wait_for_data(inputs, timeout)
		if readable:
			ack, fin_ack_recv, windows = handle_pkt(readable, ack, windows, f_log)

		if len(windows) == 0:
			continue

		# timeout check
		if (datetime.now() - windows[0][WIN_TIME]) > timedelta(seconds=timeout):
			global total_retrans
			total_retrans += len(windows)
			total_retrans -= fin_sent
			read_new_data = 1
			f.seek(windows[0][WIN_SEQ], 0)
			seq = windows[0][WIN_SEQ]
			windows = []
			fin_sent = 0

	print 'Delivery completed successfully'
	print 'Total bytes sent = ',total_bytes_sent
	print 'Segments sent = ',total_seg_sent - total_retrans
	print 'Segments retransmitted= ',total_retrans
	f.close()
	s.close()
	f_log.close()

if __name__ == '__main__':
	main()
