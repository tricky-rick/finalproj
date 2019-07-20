#!/usr/bin/python
################################################################################
#		Author: 				Patrick Earl
#		Filename:				server.py
#		Purpose:				Client application that connects to the chat
#					server. Sends commands to the server and is able to send
#					and receive messages. Using select system call to know 
#					which stream is has data ready. This will only run on 
#					UNIX systems, as windows doesn't provide this functionality,
#					go figure. This cannot run on any machine with a python 
#					version less than 2.6. Python version 2.7 is okay too. 
################################################################################

import socket # Sockets
import select # We can cleanly select which stream to listen too
import sys # To get command line arguments 
from utils import writemsg, readmsg # Utils read and write functions

# Entry point to the program... 
def main():	
	# port_Number = socket.ntohs(55510) # Default Port Number

	# Command line arguments get processed here
	if len(sys.argv) == 3: # If a port name and hostname is passed
		hostname = sys.argv[1]
		port_number = int(sys.argv[2])
		# port_Number = socket.htons(int(sys.argv[2]))
	
	elif len(sys.argv) == 2: # Hostname passed 
		hostname = sys.argv[1]
	
	else: # Incorrect number of arguments, show usage cause 
		print("Error, Incorrect number of arguments!")
		print("Usage: %s <hostname> [port number]" % sys.argv[0])
		sys.exit(-1)
	
	print("Port Number: %i" % port_Number)
	# print("NTOHS: %i" % socket.ntohs(port_Number))

	# Create the socket (IPv4, TCP)

	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# Set the socket time out to 1 minute so that the user has the 
		# time to set their username. Assuming the user doesn't disappear 
		# when they first connect. The timeout will be handled by server 
		# check ups after connection 
		
	# Catch the error if os can't create socket 
	except socket.error:
		e = sys.exc_info()[1] 
		print("Error: Failed to create socket. Message below:")
		print(e)
		sys.exit(-1)
	
	# Convert hostname to IP address and store in host
	try: 
		host = socket.gethostbyname(hostname)
	
	except socket.error:
		e = sys.exc_info()[1] 
		print("Error: Hostname invalid or doesn't exist!")
		print(e)
		sys.exit(-1)
	
	print("Connecting to %s, please wait..." % hostname)
	
	# Connect to the host now
	try:
		sock.connect((host, port_Number))
		
	except socket.error:
		e = sys.exc_info()[1]
		print("Error, Could not connect to host!")
		print(e)
		sys.exit(-1)



	# This is for the select function. We are waiting for "input" from the 
	# socket and user. Select lets us know when we recieved one and let us 
	# handle it from there. This won't be used until after the server sends
	# "READY" 
	inputs = [sock, sys.stdin] 
	
	# Store the user's nickname 
	nickname = ''
	
	# ready variable for when the server is ready to start recieving messages
	ready = False
	
	while not ready:
		try: 
			# Read in the message and store it in data 
			data = readmsg(sock)
			
			# If we get no data from server, the connection timed out
			# raise the socket.timeout exception
			if data == None:
				raise socket.timeout
				
			# Look for "ERROR" message form server, print our error if we get it
			elif "ERROR" in data:
				msg = data.split(' ', 1)
				print("Server sent error message:\n %s" % msg[1])
			
			# Server sent "HELLO", we can now send a nickname
			elif "HELLO" in data:
				nickname = send_Nickname(sock)
			
			# Server sent "RETRY", which means the user's nickname was not 
			# accepted. Prompt user for another one
			elif "RETRY" in data:
				print("Sorry nickname not valid or already in use!")
				nickname = send_Nickname(sock)
			
			# Server sent "READY", nickname was accepted. Set "ready" to true
			# and prepare to chat
			elif "READY" in data:
				print("Nickname accepted, ready to chat!")
				print("Use CTRL-C or Type '/quit' to close the client")
				ready = True
		
		# if socket times out, this exception gets raised
		except socket.timeout: 
			print("Server timed out! Closing program...")
			break; 
	
	user_Message(nickname)
	
	while ready: 	
		
		# Need to catch a KeyboardInterrupt, security is always important
		# (CTRL-C is a good way to break programs and cause issues) 
		try: 
			# The select.select function returns triple of lists. The readable 
			# sockets, the writeable sockets, and exceptional condtion sockets" 
			# We only need the readable ones
			read, write, exception = select.select(inputs, [], []) 
			
			
			for input in read:
				
				# If input is our socket connected to the server then we recieved
				# data from the server. The application process it in our 
				# process_Message function 
				if input is sock:
					data = readmsg(input) 
					
					# Server didn't return anyting, close down the application
					if data is None:
						print("Connection has been lost to the server")
						print("Application will now close...")
						ready = False
						break
					
					# The server has sent the SHUTDOWN command, which means 
					# the server is shutting down...  
					elif "SHUTDOWN" in data:
						print("\rServer is shutting down! Chat will now close, goodbye")
						writemsg(sock, "BYE") 
						ready = False
						break

					else:
						process_Message(input, data, nickname)
				
				# If the input isn't from the server socket then its user input
				# Check if its a message or a command 
				else: 
					msg = sys.stdin.readline()

					# If there is a slash in the text and its at the first index(0) 
					# then the user is sending a command 
					if "/" in msg and msg.index("/") is 0:
						msg = msg.lower()
						# If it's the quit command, close the chat client
						if  "quit" in msg:
							print("Applicaiton will now exit, goodbye!") 
							# Tell the server good bye 
							writemsg(sock, "BYE") 
							ready = False
							break 

					# Otherwise it is just a message	
					else: 
						writemsg(sock, "MSG " + msg)
						user_Message(nickname)
			
		# Just do the same thing as a '/quit' command 	
		except KeyboardInterrupt:
			print("\nApplication will now exit, goodbye!") 
			writemsg(sock, "BYE") 
			ready = False 
			break 
			
	sock.close()
	
	
################################################################################
#	Function Name:	send_Nickname		
#	Purpose:		Send the nickname to server for validation
#	Parameters:		The socket used to communicate with server
#	Returns:		string - Returns the nickname the user entered
################################################################################	
def send_Nickname(sock):
	print("Please enter a nickname (Only alphabetical characters are accepted!)")
	nick = raw_input("-> ")
	writemsg(sock, "NICK " + nick)
	return nick
		
################################################################################
#	Function Name:	user_Message
#					message. It then flushes it. 
#	Purpose:		Writes out to the stdout stream to have the user input a 
#	Paramters:		nick - The user's nickname
#	Returns: 		N/A  
################################################################################
def user_Message(nick):
    sys.stdout.write('<' + nick + '> ')
    sys.stdout.flush()		
	
def process_Message(sock, data, nickname):
		# Debugging - Remove 
		#print("prcess_Message: " + data)
	
		# This is message data, print it to the stdout
		if "MSG" in data:
			msg = data.split(' ', 1) # Split the "MSG" command from the rest
			sys.stdout.write(msg[1]) # Print the actual message
		
		# Another user has joined the server 
		elif "JOIN" in data:
			msg = data.split(' ', 1) 
			sys.stdout.write("\r" + msg[1] + " has joined the chat!\n") 
			

		# A user has timed out from the server 
		elif "TIME" in data: 
			msg = data.split(' ', 1) 
			sys.stdout.write("\r" + msg[1] + " has timed out\n") 

		elif "LEAVE" in data: 
			msg = data.split(' ', 1) 
			sys.stdout.write("\r" + msg[1] + " has left the chat!\n") 
		
		user_Message(nickname) 
		
if __name__ == "__main__":
	try:
		main() # Start Program 
	except KeyboardInterrupt:
		raise