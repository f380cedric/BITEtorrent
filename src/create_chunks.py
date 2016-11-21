import os
import sys
import math
import hashlib
import configparser

CHUNK_SIZE = 512 * 1024 # 512 kB

root_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
files_path = os.path.join(root_path, 'files')
chunks_path = os.path.join(root_path, 'chunks')
config_path = os.path.join(root_path, 'config')

class CreateChunks:
    def __init__(self):
        self.parse_args()
        self.create_chunks()
        self.create_config_file()
        print('Done')

    def parse_args(self):
        if len(sys.argv) < 2:
            print('Error: missing filename')
            sys.exit(1)
        self.filename = sys.argv[1]
        self.filepath = os.path.join(files_path, self.filename)

    def create_chunks(self):
        if not os.path.exists(self.filepath):
            print('Error: file does not exist')
            sys.exit(1)
        self.remove_existing_chunks()
        self.chunks = []
        self.chunks_peers = []
        chunks_count = math.ceil(os.path.getsize(self.filepath) / CHUNK_SIZE)
        with open(self.filepath, 'rb') as f:
            while True:
                chunk_content = f.read(CHUNK_SIZE)
                if len(chunk_content) == 0:
                    break
                chunk_hash = hashlib.sha1(chunk_content).hexdigest()
                self.chunks.append(chunk_hash)

                if len(self.chunks) <= math.ceil(chunks_count / 3):
                    peers = ['alice']
                elif len(self.chunks) <= math.ceil(chunks_count * 2 / 3):
                    peers = ['alice', 'bob']
                else:
                    peers = ['bob']
                self.chunks_peers.append(peers)

                for peername in peers:
                    with open(os.path.join(chunks_path, peername, chunk_hash + '.bin'), 'wb') as cf:
                        cf.write(chunk_content)

    def remove_existing_chunks(self):
        for peername in ['alice', 'bob', 'charlie']:
            path = os.path.join(chunks_path, peername)
            for filename in os.listdir(path):
                if filename[-4:] == '.bin':
                    os.unlink(os.path.join(path, filename))

    def create_config_file(self):
        config = configparser.ConfigParser()
        config.add_section('description')
        config.set('description', 'filename', self.filename)
        config.set('description', 'chunks_count', str(len(self.chunks)))
        config.add_section('chunks')
        for (i, chunk_hash) in enumerate(self.chunks):
            config.set('chunks', str(i), chunk_hash)
        config.add_section('chunks_peers')
        for (i, peers) in enumerate(self.chunks_peers):
            config.set('chunks_peers', str(i), ', '.join(peers))
        with open(os.path.join(config_path, 'file.ini'), 'w') as f:
            config.write(f)

if __name__ == '__main__':
    CreateChunks()
