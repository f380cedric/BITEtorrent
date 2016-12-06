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
    def __init__(self,name):
        threading.Thread.__init__(self)
        self.name = name

        config = configparser.ConfigParser()
        config.read('../config/peers.ini')
        self.addresses = {}
        for key in config.sections():
            self.addresses[key] = (config[key]['ip_address'], int(config[key]['port_number']))

        mychunks = os.listdir('../chunks/' +name)
        config.read('../config/file.ini')
        self.chunks = {'alice':[],'bob':[],'alice, bob':[]}
        for key in config['chunks']:
            if config['chunks'][key]+".bin" not in mychunks:
                self.chunks[config['chunks_peers'].get(key)].append(config['chunks'][key])
        print(self.chunks)
        #self.lock
    def run(self):
        return
        while True:

            """
        lock.acquire()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.s:
            # JUST FOR TESTING
            for key in self.chunks:
                peer = self.chunks

            self.s.connect(self.addresses[self.chunks['6e14c28263c0b81a4bb70ddbc3c504be5bc8f4e8'][0]])
            result = self.chunk_request('6b14c28263c0b81a4bb70ddbc3c504be5bc8f4e8',self.addresses[self.chunks['6e14c28263c0b81a4bb70ddbc3c504be5bc8f4e8'][0]])
            if struct.unpack("!BBHLHH",result)[1] == 6 :
                self.chunk_request('6e14c28263c0b81a4bb70ddbc3c504be5bc8f4e8',self.addresses[self.chunks['6e14c28263c0b81a4bb70ddbc3c504be5bc8f4e8'][0]])
                """
        lock.release()

    def chunk_request(self, chunk_hash, client):
        self.s.send(self.chunk_message_generator(chunk_hash))
        return self.s.recv(5120000)
        # WIP

    def chunk_message_generator(self,chunk_hash):
        if os.path.isfile("../chunks/"+self.name+"/"+chunk_hash+".bin"):
            return 0
        msg_length = 7
        fmt_content = "!20s"

        header = struct.pack("!BBHL",1,4,0,msg_length)
        message_content = struct.pack(fmt_content,bytes.fromhex(chunk_hash))

        return header+message_content