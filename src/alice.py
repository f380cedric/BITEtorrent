# Alice act as a server, she'll provide on request the chunks that Charlie need.

# She needs to read the config/peers.ini file to know her IP address and port number.

# To know wich chunks she have, alice need to read the /chunks/alice/*.bin files.

# She'll listen for incomming request on her IP/port address.

# When she receive a message :

####### If the message is invalid : ERROR INVALID_MESSAGE_FORMAT
# ie : | 1 | 6 | ? | INVALID_MESSAGE_FORMAT |

####### If the message is not a GET_CHUNK : ERROR  INVALID_REQUEST

####### If she doesn't have the chunk : ERROR CHUNK_NOT_FOUND
## (look to the directory content) !!

####### Otherwise : CHUNK message

# Known problems :
# 
# sendall or send ?
# Accept one connection at a time (=> multithreading ?)
# Stop listening after one connection (=> while True:)
#
# ../config/peers.ini => rootpath
from lib.peers import peers

alice = peers('alice')
#alice.generate_chunk_message(0xa2f9fc503534324c035b8ff21a465a5b25726a1d)
#alice.start()
