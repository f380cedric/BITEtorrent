import os
import socket
import configparser
import struct

mychunks = os.listdir('../chunks/charlie')
config = configparser.ConfigParser()
config.read('../config/file.ini')
chunks = {}
for key in config['chunks']:
    if config['chunks'][key]+".bin" not in mychunks:
        chunks[config['chunks'][key]] = (config['chunks_peers'].get(key)).split(',')
