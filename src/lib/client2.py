#!/usr/bin/python3

import os
import struct
import socket
import configparser
import threading
import queue
import binascii
import math
from lib.client import client
from merge_chunks import MergeChunks

class client2(client):
    def __init__(self,name):
        super().__init__(name)
        self.mychunks = os.listdir('../chunks/' +name)
        config = configparser.ConfigParser()
        config.read('../config/peers.ini')
        self.tracker = (config['tracker']['ip_address'], int(config['tracker']['port_number']))

    def start(self):
        """ Start the client """
        print('\nWelcome to BITEtorrent\n\nContacting tracker:')
        data = self.tracker_com()
        if data == False:
            print('ERROR NO DATA')
            return
        print('Done\n\nStarting download:\n')
        self.unpack_file_info(data)
        th = []
        for key in self.chunks[0]:
            th.append(threading.Thread(target=self.receptor,args = [key]))
        [i.start() for i in th]
        self.chunk_queue.join()
        for key in self.chunks[0]:
            self.chunks[0][key].put(None)
        [i.join() for i in th]
        print('\nDone\n\nMerging chunks:')
        MergeChunks()
        print('') #Fancy print



    def receptor(self,name,):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.connect(name)
            while True:
                chunk_hash = False
                while chunk_hash == False:
                    try:
                        chunk_hash = self.chunks[0][name].get_nowait()
                    except queue.Empty:
                        for key in self.chunks[1]:
                            try:
                                if name in key:
                                    self.chunks[0][name].put(self.chunks[1][key].get_nowait())
                                    break
                            except queue.Empty:
                                pass
                if chunk_hash is None:
                    break
                result = self.chunk_request(chunk_hash, s)
                if self.is_chunck_not_found(result):
                    print('Chunk not found in',name,'directory')
                    providers = self.providers[chunk_hash]
                    providers.remove(name)
                    if len(providers) == 0:
                        print('ERROR NO PROVIDER')
                        exit()
                    print('Chunk will be added to',providers[0],'queue')
                    self.chunks[0][providers[0]].put(chunk_hash)
                elif result == False:
                    break
                else:
                    with open("../chunks/"+self.name+"/"+chunk_hash+".bin",'wb') as file:
                        file.write(self.content(result))
                        self.chunk_queue.task_done()
                        self.chunk_queue.get()
                    print('[',math.ceil((self.number_of_chunks - self.chunk_queue.qsize())*100/self.number_of_chunks),'%] ',name,' ',len(result),' ',chunk_hash,sep='')
    def tracker_com(self):
        """ Send a GET_FILE_INFO message. Return the FILE_INFO message. """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.connect(self.tracker)
            s.send(self.get_file_info())
            data = bytes()
            while len(data) < 8:
                result = s.recv(524288)
                data += result
                if not result:
                    s.close()
                    print('Connection close')
                    return False
            length = int(struct.unpack("!BBHL",data[0:8])[3])*4
            while len(data) < length:
                result = s.recv(524288)
                data += result
                if not result:
                    s.close()
                    print('Connection close')
                    return False
        return data

    def unpack_file_info(self, data):
        """ Take the FILE_INFO as an argument. """
        self.chunks = [{},{}]
        self.providers = {}
        data = data[8::]
        chunks_count, filename_length = map(int,struct.unpack('!2H', data[:4]))
        self.number_of_chunks = chunks_count
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
                    self.providers[chunk_hash].append((ip, port))
                    peers = peers + ((ip,port),)
                if len(peers) == 1:
                    peers = peers[0]
                    if peers in self.chunks[0]:
                        self.chunks[0][peers].put(chunk_hash)
                    else:
                        self.chunks[0][peers] = queue.Queue()
                        self.chunks[0][peers].put(chunk_hash)
                else:
                    if peers in self.chunks[1]:
                            self.chunks[1][peers].put(chunk_hash)
                    else:
                        self.chunks[1][peers] = queue.Queue()
                        self.chunks[1][peers].put(chunk_hash)
                    for peer in peers:
                        if peer not in self.chunks[0]:
                            self.chunks[0][peer] = queue.Queue()

        self.chunk_queue = queue.Queue()
        list(map(self.chunk_queue.put, self.providers.keys()))