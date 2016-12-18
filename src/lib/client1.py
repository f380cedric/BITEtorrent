#!/usr/bin/python3

import configparser
from lib.client import Client

class Clientv1(Client):
    def __init__(self,name):
        super().__init__(name)
        config = configparser.ConfigParser()
        config.read('../config/peers.ini')
        self.tracker = (config['tracker']['ip_address'], int(config['tracker']['port_number']))
        config.remove_section('tracker')
        addresses = {}
        for peer in config.sections():
            addresses[peer] = (config[peer]['ip_address'], int(config[peer]['port_number']))
        config.read('../config/file.ini')
        for number in config['chunks']:
            chunk_hash = config['chunks'][number]
            if chunk_hash +".bin" not in mychunks:
                self.providers[chunk_hash] = []
                peers = tuple(map(addresses.get,map(str.strip,config['chunks_peers'][number].split(','))))                
                self.create_queues(chunk_hash,peers)
        self.chunks_count = config['description']['chunks_count']

    def start(self):
        super().start()