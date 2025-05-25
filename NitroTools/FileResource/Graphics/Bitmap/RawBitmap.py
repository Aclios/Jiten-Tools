from NitroTools.FileSystem import EndianBinaryReader
from NitroTools.FileResource.Graphics.Bitmap.Bitmap import Bitmap

class RawBitmap(Bitmap):
    '''
    Load a raw bitmap. It must be associated with at least a RawPalette, and may require a RawTilemap.

    .. warning::
        If you pass an EndianBinaryReader, it will use all the data until the end of the file; if you pass a path,
        it will use the entirety of the data of the file. Read the file yourself and pass bytes/bytearray if this
        behavior is a problem.

    :params inp: The input can either be an active EndianBinaryReader (if you want to read from an opened file), 
        a bytes or bytearray stream, or a path to a file in your system.
    '''
    def read(self, f : EndianBinaryReader):
        self.data = f.read()
        self.data_size = len(self.data)

    def get_data(self) -> bytes:
        return self.data
    
    def set_data(self, data : bytes):
        self.data = data
        self.data_size = len(self.data)
    
    def to_bytes(self):
        return self.data