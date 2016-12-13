import os
import socket
import configparser
import struct
import threading
import queue

class client():
    def __init__(self,name):
        self.name = name
        mychunks = os.listdir('../chunks/' +name)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.connect(('127.0.0.1',8000))
            print(s.send(self.get_file_info()))
            exit()
        #self.lock
    def get_file_info(self):
        return struct.pack("!BBHL",1,2,0,2)
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
                    if self.is_chunck_not_found(result):
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
        data = bytes()
        while len(data) < 8:
            result = sock.recv(524288)
            data += result
            if not result:
                sock.close()
                print('Connection close')
                return False
        length = int(struct.unpack("!BBHL",data[0:8])[3])*4
        while len(data) < length:
            result = sock.recv(524288)
            data += result
            if not result:
                sock.close()
                print('Connection close')
                return False
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