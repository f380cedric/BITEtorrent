import os
import socket
import configparser
import struct
import threading
import queue
import binascii

class client2:
    def __init__(self,name):
        self.name = name
        self.mychunks = os.listdir('../chunks/' +name)
        config = configparser.ConfigParser()
        config.read('../config/peers.ini')
        self.tracker = (config['tracker']['ip_address'], int(config['tracker']['port_number']))
        #self.tracker = ('164.15.76.104', 8000)
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

    def start(self):
        """ Start the client """
        data = self.tracker_com()
        if data == False:
            print('ERROR NO DATA')
            return
        self.unpack_file_info(data)
        for key in self.chunks[0]:
            th = threading.Thread(target=self.receptor,args = [key])
            th.start()
        self.chunk_queue.join()
        for key in self.chunks[0]:
            self.chunks[0][key].put(None)

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


    def get_file_info(self):
        """ Generate the GET_FILE_INFO message. """
        return struct.pack("!BBHL",1,2,0,2)

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
                    print(name,len(result),chunk_hash)
                    with open("../chunks/"+self.name+"/"+chunk_hash+".bin",'wb') as file:
                        file.write(self.content(result))
                        self.chunk_queue.task_done()

    def chunk_request(self, chunk_hash, sock):
        """ Send a GET_CHUNK message to the peer.
            Return the received message. /!\ Can be ERROR or CHUNK.
        """
        sock.send(self.get_chunk_message_generator(chunk_hash))
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

    def get_chunk_message_generator(self,chunk_hash):
        """ Generate the GET_CHUNK message. """
        if os.path.isfile("../chunks/"+self.name+"/"+chunk_hash+".bin"):
            return 0
        return struct.pack("!BBHL20s",1,4,0,7,bytes.fromhex(chunk_hash))

    @staticmethod
    def is_chunck_not_found(message):
        """ Check if the message to determine if it is a CHUNK_NOT_FOUND.
            Returns True if:
                - the message type is 6 (ERROR)
                - the error_code is 2 (CHUNK_NOT_FOUND) 
        """
        if (struct.unpack("!BBHL",message[0:8])[1] == 6):
            if (struct.unpack("!BBHLHH",message)[4] == 2):
                return True
        return False

    @staticmethod
    def content(message):
        """ Take a CHUNK message in argument and return only the chunk_content """
        chunk_content_length = struct.unpack("!BBHL20sL",message[0:32])[5]
        return message[32:32+chunk_content_length]