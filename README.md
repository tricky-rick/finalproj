# Kutztown University Undergraduate Client/Server Chat Server 
## Author: Patrick Earl  
### Multi-Threaded Server and Client for chat purposes built using Python2
#### Does not run on Windows Machines, meant for linux only

---
### **DO NOT USE THIS FOR ACADEMIC DISHONESTY**
Feel free to look at the code for inspiration, but I am providing this code for archival purposes. 

--- 

The goal of this assignment was to create a multi-threaded server that could handle multiple clients. My professor provided a protocol to follow to handle connecting clients, setting of a client's nickname and so forth.  

### Server Tidbits:
Every client had it's own thread dedicated to handling communications on it's socket after the initial connection was received. 

Transport layer protocol used is TCP as specified in the original program handout. 

### Client Tidbits:
The *select* system call was used to listen for messages from the server and receive input from the stdin. If messages came from the server while the user was typing a message, it would be cut off the by the message 

### Misc.

Unfortunately I cannot find the assignment handout, so this is all typed out from memory.

The original due date for the project was December 5, 2016

Project received an "A", even with some extra credit for being turned in early and with original functionality in assignment handout being met.

--- 
### How to run:

(Instructions developed using a machine running Ubuntu 19.04)

1) Launch server using: python2 server.py
    - Optional parameter: *port number*
        - Provide a port number to listen on
2) Once setup, launch clients in a separate terminal or separate machine that doesn't have a firewall blocking access to the machine running the server
    - python2 client.py **hostname**
        - Host name being the name printed out by the server at startup
    - Optional parameter: *port number*
        - If you specified a different port number for the server, enter it here
3) **Side note**: Port numbers were assigned to us the students for the project, so I hard coded mine in to reduce typing on my end. But also provided the ability to set one at startup in case the socket didn't close properly during my development :-)
4) If the client connects successfully, you will be prompted to enter a nickname for your client
    - Nicknames cannot be repeated and must be alpha-characters only
    - Instructions are printed on how to quit, but otherwise type your message and hit "enter" to send a message to all other connected clients
5) Server will keep running if all clients disconnect. To shutdown the server, press Ctrl-C which will start the clean up process.
    - Server tells all clients (if any) that the server is shutting down
    - Server waits for all threads to return and shuts down


--- 

Again please don't use this for your own project, it isn't right. 

Any questions, comments, concerns? Contact me or leave an issue.  
Again this project is here for archival purposes and is not actively developed :-) 