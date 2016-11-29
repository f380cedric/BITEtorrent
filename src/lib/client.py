import os
import socket
import configparser
import struct

class client:
    def __init__(self,name):
        config = configparser.ConfigParser()
        config.read('../config/peers.ini')

        self.addresses = {}
        for key in config.sections():
            self.addresses[key] = [config[key]['ip_address'], config[key]['port_number']]
        self.name = name
        self.ip = '0'
        self.port = '0'
        mychunks = os.listdir('../chunks/'+self.name)
        config = configparser.ConfigParser()
        config.read('../config/file.ini')
        self.chunks = {}

        for key in config['chunks']:
            if config['chunks'][key]+".bin" not in mychunks:
                self.chunks[config['chunks'][key]] = (config['chunks_peers'].get(key)).split(',')




def get_chunk_message(self,chunk_hash):
    if os.path.isfile("../chunks/"+self.name+"/"+chunk_hash+".bin"):
        return 0
    msg_length = 7
    fmt_content = "!20s"

    header = struct.pack("!BBHL",1,4,0,msg_length)
    message_content = struct.pack(fmt_content,bytes.fromhex(chunk_hash))

    return header+message_content