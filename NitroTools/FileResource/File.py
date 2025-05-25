from NitroTools.FileSystem import EndianBinaryReader, EndianBinaryFileReader, EndianBinaryStreamReader
from pathlib import Path

class File:
    def __init__(self, inp : EndianBinaryReader | bytes | bytearray | str | Path):
        if isinstance(inp, (str, Path)):
            with EndianBinaryFileReader(inp) as f:
                self.read(f)

        elif isinstance(inp, EndianBinaryReader):
            self.read(inp)

        elif isinstance(inp, (bytes, bytearray)):
            stream = EndianBinaryStreamReader(inp)
            self.read(stream)

        else:
            raise Exception("Invalid input. Expected either str, Path, bytes, bytearray, or EndianBinaryReader.")

    def read(self, f : EndianBinaryReader):
        '''
        Reads the file and loads its data to the file object. Must be overwritten.
        '''
        raise Exception('The read method must be overwritten')
    
    def to_bytes(self) -> bytes:
        '''
        Returns the file data as bytes.
        '''
        raise Exception('The to_bytes method must be overwritten')

    def write(self, filepath : str | Path) -> None:
        '''
        Write the file to the given filepath.

        :param filepath: The destination filepath, which can be anything supported by the standard ``open`` function.
        '''
        open(filepath, mode = 'wb').write(self.to_bytes())
