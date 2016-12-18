#!/usr/bin/python3

import configparser
import binascii
from lib.client import Client


class Clientv2(Client):
    def __init__(self,name):
        super().__init__(name)
        config = configparser.ConfigParser()
        config.read('../config/peers.ini')
        self.tracker = (config['tracker']['ip_address'], int(config['tracker']['port_number']))

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
            return self.receive(s)

    def unpack_file_info(self, data):
        """ Take the FILE_INFO as an argument. """
        data = data[8::]
        self.chunks_count, filename_length = map(int,struct.unpack('!2H', data[:4]))
        data = data[filename_length + filename_length%4 + 4 ::]
        chunk_info_len, offset = 0, 0
        for i in range(chunks_count):
            offset += chunk_info_len
            chunk_hash, peers_count = struct.unpack('!20sH', data[offset:offset+22])
            chunk_info_len = 24 + peers_count * 8
            chunk_hash = bytes.decode(binascii.hexlify(chunk_hash))
            if chunk_hash+".bin" not in self.mychunks:
                self.providers[chunk_hash] = []
                peers = ()
                for j in range(peers_count):
                    *ip, port = struct.unpack('!4BH', data[offset + 24 + j*8: offset + 24 + 6 + j*8])
                    ip = ".".join(map(str, ip))
                    peers += ((ip,port),)
                self.create_queues(chunk_hash,peers)