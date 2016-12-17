import struct
import os
from lib.super import Super

class Client(Super):

    @staticmethod
    def get_file_info():
        """ Generate the GET_FILE_INFO message. """
        return struct.pack("!BBHL",1,2,0,2)

    @staticmethod
    def get_chunk_message_generator(chunk_hash):
        """ Generate the GET_CHUNK message. """
        return struct.pack("!BBHL20s",1,4,0,7,bytes.fromhex(chunk_hash))

    @staticmethod
    def chunk_request(chunk_hash, sock):
        """ Send a GET_CHUNK message to the peer.
            Return the received message. /!\ Can be ERROR or CHUNK.
        """
        sock.send(client.get_chunk_message_generator(chunk_hash))
        return self.receive()

    @staticmethod
    def is_chunck_not_found(message):
        """ Check if the message to determine if it is a CHUNK_NOT_FOUND.
            Returns True if:
                - the message type is 6 (ERROR)
                - the error_code is 2 (CHUNK_NOT_FOUND) 
        """
        if (struct.unpack("!BBHL",message[0:8])[1] == 6) & (struct.unpack("!BBHLHH",message)[4] == 2):
                return True
        return False

    @staticmethod
    def content(message):
        """ Take a CHUNK message in argument and return only the chunk_content """
        chunk_content_length = struct.unpack("!BBHL20sL",message[0:32])[5]
        return message[32:32+chunk_content_length]