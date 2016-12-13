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
        self.tracker_com()

    def tracker_com(self):
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
                    print('shit')
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
        data = self.tracker_com()
        if data == False:
            print('ERROR NO DATA')
            return
        self.unpack_file_info(data)
        for peer in iter(self.chunks.keys()):
            th = threading.Thread(target=self.receptor(conn))
            th.daemon = True
            th.start()
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

    def unpack_file_info(self, data):
        self.chunks = {}
        data = data[8::]
        chunks_count, filename_length = map(int,struct.unpack('!2H', data[:4]))
        data = data[filename_length + filename_length%4 + 4 ::]
        chunk_info_len, offset = 0, 0
        for i in range(chunks_count):
            offset += chunk_info_len
            chunk_hash, peers_count = struct.unpack('!20sH', data[offset:offset+22])
            chunk_info_len = 24 + peers_count * 8
            chunk_hash = bytes.decode(binascii.hexlify(chunk_hash))
            if chunk_hash+".bin" not in self.mychunks:
                peers = ()
                for j in range(peers_count):
                    *ip, port = struct.unpack('!4BH', data[offset + 24 + j*8: offset + 24 + 6 + j*8])
                    ip = ".".join(map(str, ip))
                    peers = peers + ((ip,port),)
                if peers in self.chunks:
                        self.chunks[peers].put(chunk_hash)
                else:
                    self.chunks[peers] = queue.Queue()
                    self.chunks[peers].put(chunk_hash)
        print(self.chunks)
    def get_file_info(self):
        return struct.pack("!BBHL",1,2,0,2)
    """
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
    def is_chunck_not_found(message):
        """ check the message, returns True if:
                - the message type is 6 (ERROR)
                - the error_code is 2 (CHUNK_NOT_FOUND) 
        """
        if (struct.unpack("!BBHL",message[0:8])[1] == 6):
            if (struct.unpack("!BBHLHH",message)[4] == 2):
                return True
        return False