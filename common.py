#!/usr/bin/python
import struct
import binascii

TCPHeader = struct.Struct('H H I I B B H H H')

ACK_BIT = 0b00010000
FIN_BIT = 0x1
INIT_SEQ = 7000
def make_header(src, dest, seq, ack, size, flags, recv_win, checksum, urg):
	values = (src, dest, seq, ack, size, flags, recv_win, checksum, urg)
	packed_data = TCPHeader.pack(*values)
	return packed_data


