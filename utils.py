#!/usr/bin/python
#pylint: disable=c,w 
################################################################################
#		Author: 				Patrick Earl
#		Creation Date:			November 28, 2016 
#		Due Date:				December 5, 2016 
#		Course:					CSC 328 - Network Programming
#		Professor Name:			Dr. Frye
#		Assignemnt:				Final Project
#		Filename:				utils.py
#		Purpose:				Functions for sending and recving messages
#					in full
################################################################################

import socket 
import struct

################################################################################
#	Function Name:		writemsg
#	Purpose: 			Pack the length of the message being sent along 
#				along with the actual message so the recieving host
#				knows how many bits to expect
#	Parameters:			sock - The socket  to send the message on 
#						msg - The message to send
#	Returns:			N/A
#
#	Code Adapted from Adam Rosenfield on stackoverflow:
#	http://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data
################################################################################
def writemsg(sock, msg):
	# So we will pack the length of the message into a structure. The pack 
	# function takes a format on how to pack the data. I will use ! for network
	# and "I" for unsigned int. The standard length for a unsigned int is 4
	# btyes. The message will then follow the packed data
	msg = struct.pack("!I", len(msg)) + msg
	# Then send this whole message
	sock.sendall(msg)
	
	
################################################################################
#	Function Name:		recvmsg
#	Purpose: 			This function will be expecting a recieved message to 
#					include it's length. It will unpack this length from the 
#					message and read until that length is reached, the function
#					has a helper function called recvall
#	Parameters: 		sock - The socket to recv the message form 
#	Returns:			msg - The recieved message - If none is returned
#					something went wrong
#
#	This function was also adapted from Adam Rosenfield on stackoverflow
#	Code can be found at same url from writemsg function 
################################################################################
def readmsg(sock):
	# First unpack the message length from the message...
	# Since we know unsigned ints to be 4 bytes long thats how much it'll read
	raw_msglen = recvall(sock, 4)
	
	# If we didn't get anything return None
	if not raw_msglen:
		return None

	# Unpack our message 	
	msglen = struct.unpack("!I", raw_msglen)[0] 
	# Now it knows the message length, we can read up to that many bytes
	return recvall(sock, msglen)
	
	
################################################################################
#	Function Name:		recvall
#	Purpose:			This is the helper message to recvmsg. Will recv up to
#				the number of bytes passed along in the argument n
#	Parameters: 		sock - The socket to recv from
#						n - The number of bytes to read
#	Returns:			data - The recieved message
#
#	Code also adapted from Adam Rosenfield on stackoverflow
#	Code can be found at same url from writemsg function 
################################################################################
def recvall(sock, n):
	# While the length of our data is less then "n" continue to recieve from the
	# socket 
	data = '' # Where we will store our total message
	while len(data) < n:
		# Have the recv function recv the number of bytes left that we are 
		# expected to recieve
		msg = sock.recv(n - len(data)) 
		
		# If no data is passed, something went wrong and we should return None
		if not msg:
			return None
		data += msg
	return data

# EOF