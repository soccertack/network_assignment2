#!/usr/bin/python
import struct
import binascii

def make_header(src, dest, seq, ack, size, flags, recv_win, checksum, urg):
	values = (src, dest, seq, ack, size, flags, recv_win, checksum, urg)
	TCPHeader = struct.Struct('H H I I B B H H H')
	packed_data = TCPHeader.pack(*values)
	return packed_data


