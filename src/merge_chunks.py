import os
import sys
import configparser

root_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
chunks_path = os.path.join(root_path, 'chunks')
config_path = os.path.join(root_path, 'config')

def chunk_path(chunk_hash):
    return os.path.join(chunks_path, 'charlie', chunk_hash + '.bin')

class MergeChunks:
    def __init__(self,filepath):
        self.read_config_file(filepath)
        if self.has_all_chunks():
            self.create_file()
            print('Done')
        else:
            print('Missing chunks')

    def read_config_file(self,filepath):
        config = configparser.ConfigParser()
        config.read(os.path.join(config_path, filepath))
        self.filename = config.get('description', 'filename')
        chunks_count = config.getint('description', 'chunks_count')
        self.chunks = [config.get('chunks', str(i)) for i in range(chunks_count)]

    def has_all_chunks(self):
        for chunk_hash in self.chunks:
            if not os.path.exists(chunk_path(chunk_hash)):
                return False
        return True

    def create_file(self):
        with open(os.path.join(chunks_path, 'charlie', self.filename), 'wb') as f:
            for chunk_hash in self.chunks:
                with open(chunk_path(chunk_hash), 'rb') as cf:
                    chunk_content = cf.read()
                    f.write(chunk_content)

if __name__ == '__main__':
    MergeChunks()
