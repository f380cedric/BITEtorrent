import os
import socket
import configparser
import struct
import threading
import queue

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
        self.chunks = {}
        for key in config['chunks']:
            if config['chunks'][key]+".bin" not in mychunks:
                dic = config['chunks_peers'].get(key)
                if dic in self.chunks:
                    self.chunks[dic].put(config['chunks'][key])
                else:
                    self.chunks[dic] = queue.Queue()
                    self.chunks[dic].put(config['chunks'][key])
        #self.lock
    def start(self):
        thread_alice = threading.Thread(target=self.receptor,args = ['alice','bob'])
        thread_bob = threading.Thread(target=self.receptor, args = ['bob','alice'])
        thread_alice.start()
        thread_bob.start()
        self.chunks['alice, bob'].join()
        self.chunks['alice'].join()
        self.chunks['bob'].join()
        for key in self.chunks:
            self.chunks[key].put(None)
        thread_bob.join()
        thread_alice.join()

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
                    if client.is_chunck_not_found(result):
                        print('Chunk not found in',name,'directory')
                        print('Chunk will be added to',other_peer,'queue')
                        self.chunks[other_peer].put(chunk_hash)
                        self.chunks[name].task_done()
                    elif result == False:
                        break
                    else:
                        print(name,len(result),chunk_hash)
                        self.chunks[name].task_done()
                except queue.Empty as e:
                    try:
                        self.chunks[name].put(self.chunks['alice, bob'].get(False))
                        self.chunks['alice, bob'].task_done()
                    except queue.Empty as e:
                        pass

    def chunk_request(self, chunk_hash, sock):
        data = bytes()
        sock.send(self.chunk_message_generator(chunk_hash))
        while True:
            result = sock.recv(524288)
            data += result
            if not result:
                sock.close()
                print('Connection close')
                return False
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

    @staticmethod
    def is_chunck(message):
        """ check the message, returns True if the message type is 5 (chunk) """
        return (struct.unpack("!BBHL",message[0:8])[1] == 5)