import os
import socket
import configparser
import struct
import binascii
import math
import threading

class tracker:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('../config/peers.ini')
        self.addresses = {}
        for key in config.sections():
            self.addresses[key] = (config[key]['ip_address'], int(config[key]['port_number']))
        self.name = 'tracker'
        self.ip = self.addresses[self.name][0]
        self.port = int(self.addresses[self.name][1])

    def start(self):
        """ Start the peers to listen to connection """
        print('Welcome to tracker Server\nSoftware developped by ChrisSoft Inc.')
        print('Server is lauched as',self.name)
        # with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        #     s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        #     s.bind((self.ip, 9000))
        #     data = bytes()
        #     print('hi')
        #     while len(data) < 8:
        #         result, address = s.recvfrom(524288)
        #         data += result
        #         if not result:
        #             print('Connection close')
        #             break
        #     print('ouf')
        #     length = int(struct.unpack("!BBHL",data[0:8])[3])*4
        #     while len(data) < length:
        #         esult, address = s.recvfrom(524288)
        #         data += result
        #         if not result:
        #             print('Connection close')
        #             break
        #     print(data)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.ip, self.port))
            print('\nServer is now bound to ip',self.ip,' and port',self.port)
            s.listen() # Number of connection that the peers will accept
            while True:
                print('Waiting for connection')
                conn, addr = s.accept()
                print('Connected by', addr)
                th = threading.Thread(target=self.handle_client(conn))
                th.daemon = True
                th.start()

    def handle_client(self, conn):
        while True:
            data = bytes()
            while len(data) < 8:
                result = conn.recv(524288)
                data += result
                if not result:
                    conn.close()
                    print('Connection close')
                    return
            length = int(struct.unpack("!BBHL",data[0:8])[3])*4
            while len(data) < length:
                result = conn.recv(524288)
                data += result
                if not result:
                    conn.close()
                    print('Connection close')
                    return
            if not tracker.check_message(data): #INVALID_MESSAGE_FORMAT
                conn.send(tracker.generate_error(0))
                print('Error #0 : invalid message format')
            elif not tracker.is_get_file_info(data): #ERROR INVALID_REQUEST
                conn.send(tracker.generate_error(1))
                print('Error #1 : invalid request')
            else:
                print('Request received for file info')
                print('sent: ',len(self.generate_file_info_message()))
                conn.send(self.generate_file_info_message())
                print('Chunk sent')
        conn.close()
        return

    def generate_file_info_message(self):
        config = configparser.ConfigParser()
        config.read('../config/file.ini')
        chunks_count = int(config['description']['chunks_count'])
        filename = config['description']['filename'].encode("UTF-8")
        filename_length = len(filename)
        padding = filename_length%4
        fmt_content = "!2H%ds%ds" %(filename_length,padding)
        message_content = struct.pack(fmt_content, chunks_count, filename_length, filename, bytes(padding))
        for chunk_number in range(chunks_count):
            chunk_hash = config['chunks'][str(chunk_number)]
            print(chunk_hash, chunks_count, filename_length, padding)
            peers = (config['chunks_peers'][str(chunk_number)]).split(',')
            peers_count = len(peers)
            message_content += struct.pack("!20s2H", bytes.fromhex(chunk_hash), peers_count, 0)
            for peer in peers:
                ip, port = self.addresses[peer.strip()]
                message_content += struct.pack('!4B2H',*map(int,ip.split('.')),port,0)
        if not len(message_content)%4 == 0 :
            print("MERDE")
            exit()
        msg_length = 2 + len(message_content)//4
        header = struct.pack("!BBHL",1,5,0,msg_length)
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
    def is_get_file_info(message):
        """ Check the request to see if it is a GET_FILE_INFO"""
        return (struct.unpack("!BBHL",message[0:8])[1] == 2) & (struct.unpack("!BBHL",message[0:8])[3] == 2)

    @staticmethod
    def generate_error(error_code):
        """ Generate the ERROR message """
        ver = 1
        msg_type = 6
        msg_length = 3
        print(struct.pack("!BBHLHH",ver,msg_type,0,msg_length,error_code,0))
        return struct.pack("!BBHLHH",ver,msg_type,0,msg_length,error_code,0)
        #return bytearray([1,6,0,0,0,0,0,3,error_code>>8&0xFF,error_code&0xFF,0,0])

tracker = tracker()
tracker.start()