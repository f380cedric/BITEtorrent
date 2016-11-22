import os
import socket
import configparser
import hashlib

class test_alice:
    def __init__(self,name):
        config = configparser.ConfigParser()
        config.read('../../config/peers.ini')
        self.name = name
        self.ip = config[name]['ip_address']
        self.port = int(config[name]['port_number'])

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', self.port))
            s.sendall(bytearray([1,4,0,6])+bytearray([0xa2f9fc503534324c035b8ff21a465a5b25726a1d >> i & 0xff for i in range(152,-1,-8)]))
            data = s.recv(5120000)
        #print('Received', repr(data))
        print(len(data))
        chunk_hash=0
        for i in range(20):
            chunk_hash = data[23-i] << 8*i | chunk_hash
        print('Chunk_Hash : ',chunk_hash)
        print('Msg_length : ',data[2]<<8|data[3])
        print('Chunk_Content_length : ',data[24]<<8|data[25])
        chunk_content = data[26:-3]
        print(chunk_content)
        chunk_hash_content = hashlib.sha1(chunk_content).hexdigest()
        print(chunk_hash_content)
        print(hex(chunk_hash)[2:])
        print(chunk_hash_content == hex(chunk_hash)[2:])

test = test_alice('bob')
test.start()