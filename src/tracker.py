import os
import configparser
import struct
import binascii
import socket
import math
import threading
from lib.super import Super

class Tracker(Super):
    def __init__(self,name='tracker'):
        super().__init__(name)
        config = configparser.ConfigParser()
        config.read('../config/peers.ini')
        self.addresses = {}
        for key in config.sections():
            self.addresses[key] = (config[key]['ip_address'], int(config[key]['port_number']))
        self.ip = self.addresses[self.name][0]
        self.port = int(self.addresses[self.name][1])
        
    def catch_UDP(self):
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('<broadcast>', 9000))
                print('Waiting for UDP')
                data, address = self.receive(s)
                if not self.check_message(data): #INVALID_MESSAGE_FORMAT
                    s.sendto(self.generate_error(0), address)
                    print('Error #0 : invalid message format')
                elif not self.is_type(data,'discover_tracker'): #ERROR INVALID_REQUEST
                    s.sendto(self.generate_error(1), address)
                    print('Error #1 : invalid request')
                else:
                    print('Request received for tracker_info')
                    print('sent: ',len(self.generate_tracker_info_message()))
                    print(address)
                    s.sendto(self.generate_tracker_info_message(),address)
                    print('Chunk sent')

    def start(self):
        """ Start the tracker to listen to connection """
        super().start()
        threading.Thread(target=self.catch_UDP, daemon = True).start()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.ip, self.port))
            print('\nServer is now bound to ip',self.ip,' and port',self.port)
            s.listen()
            while True:
                print('Waiting for connection')
                conn, addr = s.accept()
                print('Connected by', addr)
                threading.Thread(target=self.handle_client(conn), daemon = True).start()
                

    def handle_client(self, conn):
        while True:
            data = self.receive(conn)[0]
            if data == False:
                break
            if not self.check_message(data): #INVALID_MESSAGE_FORMAT
                conn.send(self.generate_error(0))
                print('Error #0 : invalid message format')
            elif not self.is_type(data,'get_file_info'): #ERROR INVALID_REQUEST
                conn.send(self.generate_error(1))
                print('Error #1 : invalid request')
            else:
                print('Request received for file info')
                print('sent: ',len(self.generate_file_info_message()))
                conn.send(self.generate_file_info_message())
                print('Chunk sent')
        print('Connection closed')
        conn.close()
        
    def generate_file_info_message(self):
        config = configparser.ConfigParser()
        config.read('../config/file.ini')
        chunks_count = int(config['description']['chunks_count'])
        filename = config['description']['filename'].encode("UTF-8")
        filename_length = len(filename)
        padding = (4-filename_length%4)%4
        print(filename_length, padding)
        fmt_content = "!2H%ds%ds" %(filename_length,padding)
        message_content = struct.pack(fmt_content, chunks_count, filename_length, filename, bytes(padding))
        print(len(message_content)%4)
        for chunk_number in range(chunks_count):
            chunk_hash = config['chunks'][str(chunk_number)]
            peers = (config['chunks_peers'][str(chunk_number)]).split(',')
            peers_count = len(peers)
            message_content += struct.pack("!20s2H", bytes.fromhex(chunk_hash), peers_count, 0)
            for peer in peers:
                ip, port = self.addresses[peer.strip()]
                message_content += struct.pack('!4B2H',*map(int,ip.split('.')),port,0)
        if not len(message_content)%4 == 0 :
            print(len(message_content), "I did something wrong")
            exit()

        msg_length = 2 + len(message_content)//4
        header = struct.pack("!BBHL",1,5,0,msg_length)
        return header+message_content

    def generate_tracker_info_message(self):
        tracker_name = self.name.encode("UTF-8")
        tracker_name_length = len(tracker_name)
        padding = (4-tracker_name_length%4)%4
        fmt_content = "!4B2H%ds%ds" %(tracker_name_length,padding)
        message_content = struct.pack(fmt_content, *map(int,self.ip.split('.')), self.port, tracker_name_length, tracker_name, bytes(padding))
        header = struct.pack("!BBHL",1,1,0, 2 + len(message_content)//4)
        return header + message_content

if __name__ == '__main__':
    tracker = Tracker()
    tracker.start()