#!/usr/bin/python
#pylint: disable=C, w
################################################################################
#		Author: 				Patrick Earl
#		Creation Date:			November 21, 2016 
#		Due Date:				December 5, 2016 
#		Course:					CSC 328 - Network Programming
#		Professor Name:			Dr. Frye
#		Assignemnt:				Final Project
#		Filename:				server.py
#		Purpose:				A server application that acts a chat server
#							waits for incoming messages and repeats them to all 
#							clients. This cannot run on any machine with a 
#							python version less than 2.6. Python version 2.7 
#							is okay too.
################################################################################

import socket # Socket Library
import sys # For cli args
import threading
from time import sleep, time # For pausing certian threads and timing clients
from utils import writemsg, readmsg # Utils read and write functions


connected_clients = [] 	# A list that will hold a list of a connected clients
						# information. (i.e. It's thread ID, socket descriptor,
						# client nickname, etc)

		# The item in a client list will always be stored as 
		# 0) socket descriptor
		# 1) thread id
		# 2) client nickname
		# 3) Connected bool

# This might be repeative 
current_threads = [] # An empty list to just hold all the threads

SHUTDOWN = False # When the server is told to shutdown this will be set to True 

def main(): # Program Entry 

	# Port number used if user doesn't specify at start-up  
	port_Number = socket.htons(55510)
	global SHUTDOWN
	
	# Check if the user passed an argument, if its more than one
	# a port number was passed.
	if len(sys.argv) > 1:
		port_Number = socket.htons(int(sys.argv[1]))
	
	print("Port number: %i" % port_Number)
	print("NTOHS: %i" % socket.htons(port_Number))

	#Create the socket, bind, and make the passive passive
	try:
		# Creating Socket
		servsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		# Bind the socket
		servsock.bind((socket.gethostname(), port_Number))
		
		# Make socket passive 
		servsock.listen(5)
		
	except socket.error:
		e = sys.exc_info()[1] 
		print(" An error occured!\n%s" % e)
		exit(-1)
	
	print("Server started and listening on %s:%s" % 
			(socket.gethostname(), port_Number)) 
	
	# Now we go into a loop and start accepting connections
	while not SHUTDOWN: 
		try: 
			# We have an incoming connection, accept it
			(clientsock, clientaddr) = servsock.accept()
			
			
			# Create a new client list following specs from above. 
			# The thread id is to NOne as a place holder 
			client_list = [clientsock, None, '', True] 
			
			# Define an index to insert at, if one can't be found keep it -1
			# which python will just insert it at the end anyway
			idx = -1
			# Find the first open element in the connected_clients list 
			for c in connected_clients: 
				if c[3] is False:
					idx = connected_clients.index(c) 	
					continue			

			# If no open element was found, point idx to the end of the list
			if idx is -1: 
				idx = len(connected_clients) 	

			connected_clients.insert(idx, client_list) 		

			# Declare the clientthread and pass the list via args
			client_thread = threading.Thread(target=client_handler, 
												args=(connected_clients[idx], ))

			# Add the client's thread to the list of threads 
			current_threads.insert(idx, client_thread)
			
			# Add the thread id to the list 						
			connected_clients[idx][1] = client_thread
			
			# Start the thread
			client_thread.start()

		# If the exception is a KeyboardInterrupt(CTRL-C) begin to shutdown 
		# the server. 10 seconds should be enough time to clean up all the 
		# clients 
		except KeyboardInterrupt: 
			print("\nServer Shutting down - Closing in 10 seconds\n")
			serverShutdown(servsock)

		# If we get to this, something else went wrong... 
		# We'll print the error and break the loop
		except:
			print "Error: ", sys.exc_info()[0]
			break
	
	# If the application gets here, it'll attempt to join all the threads
	# and close down any sockets. The server is not closing gracefully 
	for c in connected_clients:
		broadcastMessage(-1, "CLOSE") 
		c[1].join()
		c[0].close()
		
	servsock.close()
	sys.exit(-1)

################################################################################
#		Funciton Name:		client_Handler
#		Purpose:			Thread handler for clients. Handles all 
# 							communication for client. 
# 		Parameter:			clist - The list containing all the information 
# 							for the client. 
#		Returns:			N/A 
###############################################################################

def client_handler(clist): 
	
	# clist should have the following stucture:
	# [0] - socket descriptor
	# [1] - thread id 
	# [2] - client nickame 
	# [3] - Client Connected True or False
	
	global SHUTDOWN
	idx = connected_clients.index(clist)

	# Set the client's socket timeout to 30 minutes '
	clist[0].settimeout(1800)

	# Send the hello message to the client
	writemsg(clist[0], "HELLO")

	# Loop while the client is still connected.. 
	while clist[3]: 

		try: 
			# Debugging - Remove 
			#print("CLIENT LOOP")
		
			# Read in the message and store it in data
			data = readmsg(clist[0])

			# If no data is recieved from server, connection was closed..
			if data is None:
				print("Client %i has timed out..." % idx) 
				broadcastMessage(clist, "TIME " + clist[2])
				break
			
			# The client sent us a nickname, time to process it 
			elif "NICK" in data:
				nick = data.split() # Split the nickname from the command
				
				# If the length is longer than two, that means the user attempted 
				# to put a space in their nickname which isn't allowed
				if len(nick) > 2: 
					writemsg(clist[0], "RETRY")
				
				# If the nickname contains anything but alpha characters its not 
				# acceptable. User has to try again
				elif not nick[1].isalpha():
					writemsg(clist[0], "RETRY")
					
				# Check that the nickname is not already in use...	
				elif check_nick_in_use(nick[1]): 
					writemsg(clist[0], "RETRY") 
					
				else:
					clist[2] = nick[1]
					writemsg(clist[0], "READY")
					broadcastMessage(clist, 
									"JOIN " + nick[1]) 
			
			elif "MSG" in data: 
				msg = data.split(' ', 1) 
				broadcastMessage(clist, 
							"MSG \r<" + clist[2] + "> " + msg[1])
				
			# If recieve by from client, the client is diconnectecting	
			elif "BYE" in data: 
				print("Client %i disconnecting." 
							% connected_clients.index(clist))
				broadcastMessage(clist, "LEAVE " + clist[2])
				break
				
			else: 
				writemsg(clist[0], "ERROR Invalid command, connection closed")
				break 
				

		except socket.timeout: 
			print("Client %i has been timed out..." % idx) 
	
	# The client is closing at this point. Clean up the mess. 
	print("Client ID %i, closed" % idx)
	clist[3] = False # If we exited the loop the client disconnected 
	clist[2] = ''
	clist[0].close() # Close the client's socket
	current_threads.remove(clist[1])

	return

################################################################################
#		Function Name:		check_nick_in_use
#		Purpose:			Loop through clients and check that the nickname
#					is not in use
#		Parameters:			nick - the nickname to check 
#		Returns:			True - if the nickname is in use
#							False - if the nickname is not in use
################################################################################
def check_nick_in_use(nick):
	for c in connected_clients:
		if nick == c[2]:
			return True
	return False

	
################################################################################
#		Function Name:		broadcastMessage
#		Purpose:			Broadcast the message to all connected clients
#					except the id specifed by client paramteter. If -1 is 
#					passed by paramteter the message is passed to all clients
#		Parameters: 		client - The client socket not to send the message 
#									too
#							message - The message to send
#		Returns:			N/A
################################################################################	
def broadcastMessage(client, message):
	if client is -1: 
		for c in connected_clients:
			if c[3] is False:
				continue 
			else: 
				writemsg(c[0], message) 
	else:
		for c in connected_clients:
			if c[3] is False or c is client:
				continue
			else:
				writemsg(c[0], message) 

################################################################################
#		Function Name:		serverShutdown 
#		Purpose:			If the KeyboardInterrupt event gets passed in the 
#						main thread then we will handle closing the server 
#						gracefully here. 
#		Parameters:			servsock - The server's listening socket 
# 		Returns:			N/A 
# ##############################################################################'
def serverShutdown(servsock):

	# This will tell all the clients the server is shutting down 
	# Clients will respond by sending "BYE"
	broadcastMessage(-1, "SHUTDOWN") 
	
	# Close the servsock so we can't accept any new connections 
	servsock.close()

	# Let all the threads process the shutdown event. They should close their 
	# sockets after the loop breaks due to SHUTDOWN becoming true. 
	sleep(4)

	# If forever the reason the thread's can't finish before the 4 seconds 
	# are up, just join them. 
	for c in current_threads: 
		c.join() 

	# Sleep the remaining seconds and then close the server 
	sleep(6) 

	# Now close the applicaiton 
	print("Server Shutdown complete, goodbye!") 
	sys.exit() 


if __name__ == "__main__":
	main()

#EOF