#!/usr/bin/python
import struct
import binascii
from datetime import datetime

TCPHeader = struct.Struct('H H I I B B H H H')

ACK_BIT = 0b00010000
FIN_BIT = 0x1
INIT_SEQ = 0
COMMA = ', '

def make_header(src, dest, seq, ack, size, flags, recv_win, checksum, urg):
	values = (src, dest, seq, ack, size, flags, recv_win, checksum, urg)
	packed_data = TCPHeader.pack(*values)
	return packed_data

def write_log (src, dst, recv_seq, recv_ack, flags, f_log, RTT=0):
	log = unicode(datetime.now())
	log += COMMA + str(src) + COMMA + str(dst)
	log += COMMA + str(recv_seq) + COMMA + str(recv_ack)
	if (flags & FIN_BIT):
		log += COMMA + "FIN"
	if (flags & ACK_BIT):
		log += COMMA + "ACK"
	if RTT != 0:
		log += COMMA + str(RTT) + "ms"
	log += "\n"
	f_log.write(log)



