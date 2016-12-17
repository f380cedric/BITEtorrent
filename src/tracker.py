import os
import configparser
import struct
import binascii
import math
import threading
from lib.super import Super

class Tracker(Super):
    def __init__(self):
        super().__init__('tracker')
        config = configparser.ConfigParser()
        config.read('../config/peers.ini')
        self.addresses = {}
        for key in config.sections():
            self.addresses[key] = (config[key]['ip_address'], int(config[key]['port_number']))
        self.ip = self.addresses[self.name][0]
        self.port = int(self.addresses[self.name][1])

    def start(self):
        """ Start the tracker to listen to connection """
        super().start()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.ip, self.port))
            print('\nServer is now bound to ip',self.ip,' and port',self.port)
            s.listen()
            while True:
                print('Waiting for connection')
                conn, addr = s.accept()
                print('Connected by', addr)
                th = threading.Thread(target=self.handle_client(conn))
                th.daemon = True
                th.start()

    def handle_client(self, conn):
        while True:
            data = self.receive(conn)
            if data == False
                return
            if not self.check_message(data): #INVALID_MESSAGE_FORMAT
                conn.send(self..generate_error(0))
                print('Error #0 : invalid message format')
            elif not self..is_get_file_info(data): #ERROR INVALID_REQUEST
                conn.send(self..generate_error(1))
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
            print("I did something wrong")
            exit()

        msg_length = 2 + len(message_content)//4
        header = struct.pack("!BBHL",1,5,0,msg_length)
        return header+message_content


    @staticmethod
    def is_get_file_info(message):
        """ Check the request to see if it is a GET_FILE_INFO"""
        return (struct.unpack("!BBHL",message[0:8])[1] == 2) & (struct.unpack("!BBHL",message[0:8])[3] == 2)



tracker = tracker()
tracker.start()