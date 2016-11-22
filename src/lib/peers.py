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
import os
import socket
import configparser

class peers:
    def __init__(self,name):
        config = configparser.ConfigParser()
        config.read('../config/peers.ini')
        self.name = name
        self.ip = config[name]['ip_address']
        self.port = int(config[name]['port_number'])

    def start(self):
        """ Start the peers to listen to connection """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.ip, self.port))
            s.listen(1) # Number of connection that the peers will accept
            #while True:
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    if not peers.check_message(data): #INVALID_MESSAGE_FORMAT
                        conn.sendall(peers.generate_error(0))
                        print('Error : invalid message format. \n')
                        break
                    if not peers.is_get_chunck(data): #ERROR INVALID_REQUEST
                        conn.sendall(peers.generate_error(1))
                        print('Error : invalid request. \n')
                        break
                    if not peers.check_chunk(self,peers.chunk_hash(data)): #ERROR CHUNK_NOT_FOUND
                        conn.sendall(peers.generate_error(2))
                        print('Error : chunk not found. \n')
                        break
                    print('ok')
                    #conn.sendall(generate_chunk_message(self,peers.chunk_hash(data)))

    def check_chunk(self,chunk_hash):
        """ Check if the peer have the requested chunk """
        return os.path.isfile("../chunks/"+self.name+"/"+hex(chunk_hash)[2:]+".bin")

    def generate_chunk_message(self,chunk_hash):
        file = open("../chunks/"+self.name+"/"+hex(chunk_hash)[2:]+".bin",'rb')
        content = file.read()
        file.close()
        print(content)
        pac = bytearray(content)
        packet = bytearray([1,5, msg_length])
        return True

    @staticmethod
    def check_message(message):
        """ Check if the message is valid """
        check_chunk = False
        if not len(message)%4:
        # Multiple of 4
            if message[0] == 1:
            # Version is one
                if (message[2]<<8|message[3]) == len(message)/4:
                # body is correct size wrt msg_length
                    check_chunk = True
        return check_chunk

    @staticmethod
    def is_get_chunck(message):
        """ Check the request to see if it is a GET_CHUNK """
        return message[1]==4 & message[2]<<8|message[3] == 6

    @staticmethod
    def generate_error(error_code):
        """ Generate the ERROR message """
        return bytearray([1,6,0,2,error_code>>8&0xFF,error_code&0xFF,0,0])

    @staticmethod
    def chunk_hash(message_get_chunk):
        """ Take the GET_CHUNK message in entry and returns the chunk_hash """
        chunk_hash = 0
        for i in range(20):
            chunk_hash = message_get_chunk[23-i] << 8*i | chunk_hash
        return chunk_hash