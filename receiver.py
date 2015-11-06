#!/usr/bin/python

#reference
# http://www.binarytides.com/programming-udp-sockets-in-python/

import select
import socket
import sys
from datetime import datetime
from threading import Thread

HOST = ''
PORT = 4118
 
file_name = "received.txt"

if __name__ == '__main__':
	# Datagram (udp) socket
	try :
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		print 'Socket created'
	except socket.error, msg :
		print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
		sys.exit()
	 
	 
	# Bind socket to local host and port
	try:
		s.bind((HOST, PORT))
	except socket.error , msg:
		print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
		sys.exit()
		 
	print 'Socket bind complete'
	 
	f = open(file_name, "wb")
	#now keep talking with the client
	while 1:
		# receive data from client (data, addr)
		d = s.recvfrom(1024)
		data = d[0]
		addr = d[1]
		 
		if not data: 
			break
		 
		reply = 'OK...' + data
	   
		# TODO: send ACK
		s.sendto(reply , addr)

		#TODO: record packet headers to a log file (ordered)
		print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()
		f.write(data);
		break
	s.close()
	f.close()
