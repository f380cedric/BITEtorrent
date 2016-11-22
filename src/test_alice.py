import os
import socket
import configparser

class test_alice:
    def __init__(self,name):
        config = configparser.ConfigParser()
        config.read('../config/peers.ini')
        self.name = name
        self.ip = config[name]['ip_address']
        self.port = int(config[name]['port_number'])

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', self.port))
            s.sendall(bytearray([1,4,0,6])+bytearray([0xa2f9fc503534324c035b8ff21a465a5b25726a1d >> i & 0xff for i in range(152,-1,-8)]))
            data = s.recv(1024)
        print('Received', repr(data))