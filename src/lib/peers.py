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
        print('Welcome to Peers Server\nSoftware developped by ChrisSoft Inc.')
        print('Server is lauched as',self.name)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.ip, self.port))
            print('\nServer is now bound to ip',self.ip,' and port',self.port)
            print('Server is now ready to accept connection')
            s.listen(1) # Number of connection that the peers will accept
            #while True:
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr,'\nReady to receive request')
                while True:
                    data = conn.recv(5120000)
                    if not data:
                        break
                    if not peers.check_message(data): #INVALID_MESSAGE_FORMAT
                        conn.sendall(peers.generate_error(0))
                        print('Error #0 : invalid message format')
                        break
                    if not peers.is_get_chunck(data): #ERROR INVALID_REQUEST
                        conn.sendall(peers.generate_error(1))
                        print('Error #1 : invalid request')
                        break
                    if not self.check_chunk(peers.chunk_hash(data)): #ERROR CHUNK_NOT_FOUND
                        conn.sendall(peers.generate_error(2))
                        print('Error #2 : chunk not found')
                        break
                    print('Request received for chunk', hex(peers.chunk_hash(data))[2:])
                    conn.sendall(self.generate_chunk_message(peers.chunk_hash(data)))

    def check_chunk(self,chunk_hash):
        """ Check if the peer have the requested chunk """
        return os.path.isfile("../chunks/"+self.name+"/"+hex(chunk_hash)[2:]+".bin")

    def generate_chunk_message(self,chunk_hash):
        with open("../chunks/"+self.name+"/"+hex(chunk_hash)[2:]+".bin",'rb') as file:
            content = file.read()

        chunk_content = bytearray(content)

        print(len(chunk_content))

        while (len(chunk_content)-2)%4 != 0:
            chunk_content = chunk_content + bytearray(1) # Add 1 byte of zeros
            print('padded')

        chunk_content_length = len(chunk_content) # En bytes

        print('chunk_content_length : ',chunk_content_length)
        msg_length = 6 + 1 + ((chunk_content_length-2)//4)
        print('msg_length : ',msg_length)


        header_b = bytearray([1,5, msg_length>>8&0xFF,msg_length&0xFF])
        chunk_hash_b = bytearray([chunk_hash >> i & 0xff for i in range(152,-1,-8)])
        chunk_content_length_b = bytearray([chunk_content_length>>8&0xFF,chunk_content_length&0xFF])

        print('chunk generated')
        print('Nbr of bytes sent : ',len(header_b+chunk_hash_b+chunk_content_length_b+chunk_content))

        return header_b+chunk_hash_b+chunk_content_length_b+chunk_content
        return chunk

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
        return (message[1]==4) & (message[2]<<8|message[3] == 6)

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