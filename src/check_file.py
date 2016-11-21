import os
import sys
import configparser

root_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
files_path = os.path.join(root_path, 'files')
chunks_path = os.path.join(root_path, 'chunks')
config_path = os.path.join(root_path, 'config')

class CheckFile:
    def __init__(self):
        self.read_config_file()
        if self.check_file():
            print('Files are identical')
        else:
            print('Files are NOT identical')

    def read_config_file(self):
        config = configparser.ConfigParser()
        config.read(os.path.join(config_path, 'file.ini'))
        self.filename = config.get('description', 'filename')

    def check_file(self):
        with open(os.path.join(files_path, self.filename), 'rb') as f1:
            with open(os.path.join(chunks_path, 'charlie', self.filename), 'rb') as f2:
                while True:
                    c1 = f1.read(1)
                    c2 = f2.read(1)
                    if c1 != c2:
                        return False
                    if not c1 and not c2:
                        return True

if __name__ == '__main__':
    CheckFile()
