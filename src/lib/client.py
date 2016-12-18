import struct
import os
import threading
import math
import queue
import socket
from lib.super import Super
from merge_chunks import MergeChunks

class Client(Super):
    chunks = [{},{}]
    providers = {}
    chunks_count = 0
    filepath = 'file1.ini'
    
    def __init__(self,name):
        super().__init__(name)
        self.mychunks = os.listdir('../chunks/' +self.name)

    @staticmethod
    def get_file_info():
        """ Generate the GET_FILE_INFO message. """
        return struct.pack("!BBHL",1,2,0,2)

    @staticmethod
    def get_chunk_message_generator(chunk_hash):
        """ Generate the GET_CHUNK message. """
        return struct.pack("!BBHL20s",1,4,0,7,bytes.fromhex(chunk_hash))

    def chunk_request(self,chunk_hash, sock):
        """ Send a GET_CHUNK message to the peer.
            Return the received message. /!\ Can be ERROR or CHUNK.
        """
        sock.send(self.get_chunk_message_generator(chunk_hash))
        return self.receive(sock)[0]

    def start(self):
        super().start()
        th = []
        for key in self.chunks[0]:
            th.append(threading.Thread(target=self.receptor,args = [key], daemon = True))
        list(map(threading.Thread.start, th))
        self.chunk_queue.join()
        for key in self.chunks[0]:
            self.chunks[0][key].put(None)
        list(map(threading.Thread.join, th))
        print('\nDone\n\nMerging chunks:')
        MergeChunks(self.filepath)
        print('') #Fancy print

    def receptor(self,name):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.connect(name)
            my_queue = self.chunks[0][name]
            com_queues = []
            for key in self.chunks[1]:
                if name in key:
                    com_queues.append(self.chunks[1][key])
            while True:
                chunk_hash = False
                while chunk_hash == False:
                    try:
                        chunk_hash = my_queue.get_nowait()
                    except queue.Empty:
                        for com in com_queues:
                            try:
                                chunk_hash = com.get_nowait()
                                break
                            except queue.Empty:
                                pass
                if chunk_hash is None:
                    break
                result = self.chunk_request(chunk_hash, s)
                if result == False:
                    print('peer not responding')
                    my_queue.put(chunk_hash)
                elif self.is_type(result, 'chunk_not_found'):
                    print('Chunk not found in',name,'directory')
                    providers = self.providers[chunk_hash]
                    providers.remove(name)
                    if len(providers) == 0:
                        print('ERROR NO PROVIDER')
                    else:
                        indice = 0
                        for i in range(1,len(providers)):
                            if len(chunks[0][providers[i]].qsize()) < len(chunks[0][providers[indice]].qsize()) :
                                indice = i
                            
                        print('Chunk will be added to',providers[indice],'queue')
                        self.chunks[0][providers[indice]].put(chunk_hash)
                else:
                    with open("../chunks/"+self.name+"/"+chunk_hash+".bin",'wb') as file:
                        file.write(self.content(result))
                        self.chunk_queue.task_done()
                        self.chunk_queue.get()
                    print('[',math.ceil((self.chunks_count - self.chunk_queue.qsize())*100/self.chunks_count),'%] ',name,' ',len(result),' ',chunk_hash,sep='')

    @staticmethod
    def content(message):
        """ Take a CHUNK message in argument and return only the chunk_content """
        chunk_content_length = struct.unpack("!BBHL20sL",message[0:32])[5]
        return message[32:32+chunk_content_length]

    def create_queues(self,chunk_hash,peers):

        list(map(self.providers[chunk_hash].append,peers))
        shared = 1
        if len(peers) == 1:
            peers = peers[0]
            shared = 0
        else:
            for peer in peers:
                if peer not in self.chunks[0]:
                    self.chunks[0][peer] = queue.Queue()
        if peers in self.chunks[shared]:
                self.chunks[shared][peers].put(chunk_hash)
        else:
            self.chunks[shared][peers] = queue.Queue()
            self.chunks[shared][peers].put(chunk_hash)