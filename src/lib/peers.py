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
import struct
import binascii
import math
import threading

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
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.ip, self.port))
            print('\nServer is now bound to ip',self.ip,' and port',self.port)
            s.listen(1) # Number of connection that the peers will accept
            while True:
                print('Waiting for connection')
                conn, addr = s.accept()
                print('Connected by', addr)
                th = threading.Thread(target=self.handle_client(conn))
                th.daemon = True
                th.start()

    def handle_client(self, conn):
        data = bytes()
        while True:
            result = conn.recv(524288)
            data += result
            if not result:
                conn.close()
                print('Connection close')
                return
            length = int(struct.unpack("!BBHL",data[0:8])[3])*4
            if len(data) == length:
                conn.shutdown(0)
                break
        if not peers.check_message(data): #INVALID_MESSAGE_FORMAT
            conn.send(peers.generate_error(0))
            print('Error #0 : invalid message format')
        elif not peers.is_get_chunck(data): #ERROR INVALID_REQUEST
            conn.send(peers.generate_error(1))
            print('Error #1 : invalid request')

        elif not self.check_chunk(peers.chunk_hash(data)): #ERROR CHUNK_NOT_FOUND
            conn.send(peers.generate_error(2))
            print('Error #2 : chunk not found')

        else:
            print('Request received for chunk', peers.chunk_hash(data))
            print('sent: ',len(self.generate_chunk_message(peers.chunk_hash(data))))
            conn.send(self.generate_chunk_message(peers.chunk_hash(data)))
            print('Chunk sent')
        conn.close()
        return
    def check_chunk(self,chunk_hash):
        """ Check if the peer have the requested chunk """
        return os.path.isfile("../chunks/"+self.name+"/"+chunk_hash+".bin")

    def generate_chunk_message(self,chunk_hash):
        with open("../chunks/"+self.name+"/"+chunk_hash+".bin",'rb') as file:
            content = file.read()

        msg_length = 8 + math.ceil(len(content)/4)
        chunk_content_length = len(content)
        padding = len(content)%4
        fmt_content = "!20sL%ds%ds" %(len(content),padding)

        header = struct.pack("!BBHL",1,5,0,msg_length)
        message_content = struct.pack(fmt_content,bytes.fromhex(chunk_hash),chunk_content_length,content,bytes(padding))

        return header+message_content

    @staticmethod
    def check_message(message):
        """ Check if the message is valid """
        check_chunk = False
        if not len(message)%4:
            print('Multiple of 4 : OK')
        # Multiple of 4
            if struct.unpack("!BBHL",message[0:8])[0] == 1:
                print('Version is one : OK')
            # Version is one
                if (struct.unpack("!BBHL",message[0:8])[3]) == len(message)/4:
                    print('Correct size : OK')
                # body is correct size wrt msg_length
                    check_chunk = True
        return check_chunk

    @staticmethod
    def is_get_chunck(message):
        """ Check the request to see if it is a GET_CHUNK """
        return (struct.unpack("!BBHL",message[0:8])[1] == 4) & (struct.unpack("!BBHL",message[0:8])[3] == 7)

    @staticmethod
    def generate_error(error_code):
        """ Generate the ERROR message """
        ver = 1
        msg_type = 6
        msg_length = 3
        print(struct.pack("!BBHLHH",ver,msg_type,0,msg_length,error_code,0))
        return struct.pack("!BBHLHH",ver,msg_type,0,msg_length,error_code,0)
        #return bytearray([1,6,0,0,0,0,0,3,error_code>>8&0xFF,error_code&0xFF,0,0])

    @staticmethod
    def chunk_hash(message_get_chunk):
        """ Take the GET_CHUNK message in entry and returns the chunk_hash in string """
        return bytes.decode(binascii.hexlify(struct.unpack("!BBHL20s",message_get_chunk)[4]))
