#!/usr/bin/python3

import os
import socket
import configparser
import struct
import threading
import queue
from lib.client import client

class client1(client):
    def __init__(self,name):
        super().__init__(name)
        self.lock= {'alice':threading.Lock(), 'bob' : threading.Lock()}
        config = configparser.ConfigParser()
        config.read('../config/peers.ini')
        self.addresses = {}
        for key in config.sections():
            self.addresses[key] = (config[key]['ip_address'], int(config[key]['port_number']))

        mychunks = os.listdir('../chunks/' +name)
        config.read('../config/file.ini')
        self.chunks = {}
        for key in config['chunks']:
            if config['chunks'][key]+".bin" not in mychunks:
                dic = config['chunks_peers'].get(key)
                if dic in self.chunks:
                    self.chunks[dic].put(config['chunks'][key])
                else:
                    self.chunks[dic] = queue.Queue()
                    self.chunks[dic].put(config['chunks'][key])

    def start(self):
        thread_alice = threading.Thread(target=self.receptor,args = ['alice','bob'], daemon = True)
        thread_bob = threading.Thread(target=self.receptor, args = ['bob','alice'], daemon = True)
        thread_alice.start()
        thread_bob.start()
        self.chunks['alice, bob'].join()
        self.chunks['alice'].join()
        self.chunks['bob'].join()
        for key in self.chunks:
            self.chunks[key].put(None)
        thread_bob.join()
        thread_alice.join()

    def receptor(self,name,other_peer):
        address = self.addresses[name]
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.connect(address)
            while True:
                try:
                    chunk_hash = self.chunks[name].get(False)
                    if chunk_hash is None:
                        break
                    result = self.chunk_request(chunk_hash, s)
                    if self.is_chunck_not_found(result):
                        print('Chunk not found in',name,'directory')
                        print('Chunk will be added to',other_peer,'queue')
                        self.chunks[other_peer].put(chunk_hash)
                        self.chunks[name].task_done()
                    elif result == False:
                        break
                    else:
                        print(name,len(result),chunk_hash)
                        with open("../chunks/"+self.name+"/"+chunk_hash+".bin",'wb') as file:
                            file.write(self.content(result))
                        self.chunks[name].task_done()
                except queue.Empty as e:
                    try:
                        self.chunks[name].put(self.chunks['alice, bob'].get(False))
                        self.chunks['alice, bob'].task_done()
                    except queue.Empty as e:
                        pass