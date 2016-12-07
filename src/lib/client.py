import os
import socket
import configparser
import struct
import threading

class client():
    def __init__(self,name):
        self.name = name
        self.lock= {'alice':threading.Lock(), 'bob' : threading.Lock()}
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
        #self.lock
    def start(self):
        thread_alice = threading.Thread(target=self.receptor('alice'))
        thread_bob = threading.Thread(target=self.receptor('bob'))
        thread_alice.daemon = True
        thread_bob.daemon   = True
        thread_alice.start()
        thread_bob.start()
        while not (self.lock['alice'].locked() or self.lock['bob'].locked()):
            pass
            """
            ...lock alice

            ...lock bob

            if ...
                break
            """

        #while True:
        # lock.acquire()
        # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.s:
        #     # JUST FOR TESTING
        #     self.s.connect(self.addresses[self.chunks['6e14c28263c0b81a4bb70ddbc3c504be5bc8f4e8'][0]])
        #     result = self.chunk_request('6b14c28263c0b81a4bb70ddbc3c504be5bc8f4e8',self.addresses[self.chunks['6e14c28263c0b81a4bb70ddbc3c504be5bc8f4e8'][0]])
        #     if struct.unpack("!BBHLHH",result)[1] == 6 :
        #         self.chunk_request('6e14c28263c0b81a4bb70ddbc3c504be5bc8f4e8',self.addresses[self.chunks['6e14c28263c0b81a4bb70ddbc3c504be5bc8f4e8'][0]])
        # lock.release()

    def receptor(self,name):
        self.lock[name].acquire()
        address = self.addresses[name]
        for i in self.chunks[name]:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(address)
                result = self.chunk_request(i, s)
                print(name+'\n',len(result),'\n',i)

    def chunk_request(self, chunk_hash, sock):
        data = bytes()
        sock.send(self.chunk_message_generator(chunk_hash))
        while True:
            result = sock.recv(524288)
            data += result
            if not result:
                sock.close()
                print('Connection close')
                return
            length = int(struct.unpack("!BBHL",data[0:8])[3])*4
            if len(data) == length:
                break
        return data

    def chunk_message_generator(self,chunk_hash):
        if os.path.isfile("../chunks/"+self.name+"/"+chunk_hash+".bin"):
            return 0
        msg_length = 7
        fmt_content = "!20s"

        header = struct.pack("!BBHL",1,4,0,msg_length)
        message_content = struct.pack(fmt_content,bytes.fromhex(chunk_hash))

        return header+message_content