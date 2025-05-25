from io import BytesIO
from .EndianReader import EndianBinaryReader
from .EndianWriter import EndianBinaryWriter

class EndianBinaryUpdater(EndianBinaryReader, EndianBinaryWriter):
    def __init__(self, filepath : str, endianness : str = 'little'):
        self.set_endianness(endianness)
        self.filepath = filepath
        self.file = open(self.filepath,mode='rb+')
        self.read = self.file.read
        self.write = self.file.write
        self.tell = self.file.tell
        self.seek = self.file.seek

class EndianBinaryFileUpdater(EndianBinaryReader, EndianBinaryWriter):
    def __init__(self, filepath : str, endianness : str = 'little'):
        self.set_endianness(endianness)
        self.filepath = filepath
        self.file = open(self.filepath,mode='rb+')
        self.read = self.file.read
        self.write = self.file.write
        self.tell = self.file.tell
        self.seek = self.file.seek

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()

class EndianBinaryStreamUpdater(EndianBinaryReader, EndianBinaryWriter):
    def __init__(self,stream : bytes, endianness : str = 'little'):
        self.set_endianness(endianness)
        self.stream = BytesIO(stream)
        self.read = self.stream.read
        self.write = self.stream.write
        self.tell = self.stream.tell
        self.seek = self.stream.seek
        self.getvalue = self.stream.getvalue