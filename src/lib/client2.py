#!/usr/bin/python3


import configparser
import socket
import binascii
import struct
import queue
from lib.client import Client


class Clientv2(Client):
    def __init__(self,name):
        super().__init__(name)
        config = configparser.ConfigParser()
        config.read('../config/peers.ini')
        self.tracker = (config['tracker']['ip_address'], int(config['tracker']['port_number']))
        self.tracker = ('164.15.76.104', 8000)

    def start(self):
        """ Start the client """
        data = self.tracker_com()
        if data == False:
            print('ERROR NO DATA')
            return
        self.unpack_file_info(data)
        super().start()

    def tracker_com(self):
        """ Send a GET_FILE_INFO message. Return the FILE_INFO message. """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.connect(self.tracker)
            s.send(self.get_file_info())
            return self.receive(s)[0]

    def unpack_file_info(self, data):
        """ Take the FILE_INFO and excract the data to fill the differents queues """
        file = configparser.ConfigParser()
        list(map(file.add_section, ['description', 'chunks']))
        data = data[8::]
        self.chunks_count, filename_length = map(int,struct.unpack('!2H', data[:4]))
        filename = struct.unpack('%ds' %filename_length, data[4:4+filename_length])[0].decode('UTF-8')
        data = data[filename_length + (4-filename_length%4)%4 + 4 ::]
        file['description'] = {'filename': filename,
        'chunks_count' : self.chunks_count}
        chunk_info_len, offset = 0, 0
        for i in range(self.chunks_count):
            offset += chunk_info_len
            chunk_hash, peers_count = struct.unpack('!20sH', data[offset:offset+22])
            chunk_info_len = 24 + peers_count * 8
            chunk_hash = bytes.decode(binascii.hexlify(chunk_hash))
            file.set('chunks', str(i), chunk_hash)
            if chunk_hash+".bin" not in self.mychunks:
                self.providers[chunk_hash] = []
                peers = ()
                for j in range(peers_count):
                    *ip, port = struct.unpack('!4BH', data[offset + 24 + j*8: offset + 24 + 6 + j*8])
                    ip = ".".join(map(str, ip))
                    peers += ((ip,port),)
                self.create_queues(chunk_hash,peers)
        self.chunk_queue = queue.Queue()
        list(map(self.chunk_queue.put, self.providers.keys()))
        with open("../config/file1.ini",'w') as fileini:
                        file.write(fileini)
