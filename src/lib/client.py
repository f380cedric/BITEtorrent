import os
import socket
import configparser
import struct
import threading

# mychunks = os.listdir('../chunks/charlie')
# config = configparser.ConfigParser()
# config.read('../config/file.ini')
# chunks = {}
# for key in config['chunks']:
#     if config['chunks'][key]+".bin" not in mychunks:
#         chunks[config['chunks'][key]] = (config['chunks_peers'].get(key)).split(',')

class client(threading.Thread):
    def __init__(self,n):
        threading.Thread.__init__(self)
        self.n = n

    def run(self):
        while True:
            lock.acquire()
            print('Je suis le thread', self.n)
            lock.release()

lock = threading.Lock()
t1 = client(1)
t2 = client(2)
t1.start()
t2.start()
