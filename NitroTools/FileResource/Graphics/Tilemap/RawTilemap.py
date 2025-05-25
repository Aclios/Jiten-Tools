from NitroTools.FileSystem import EndianBinaryStreamReader, EndianBinaryStreamWriter
from NitroTools.FileResource.Graphics.Tilemap.Tilemap import Tilemap, MapData

class RawTilemap(Tilemap):
    '''
    Load a raw tilemap. It must be associated with a RawPalette and a RawBitmap.

    .. warning::
        If you pass an EndianBinaryReader, it will use all the data until the end of the file; if you pass a path,
        it will use the entirety of the data of the file. Read the file yourself and pass bytes/bytearray if this
        behavior is a problem.

    :params inp: The input can either be an active EndianBinaryReader (if you want to read from an opened file), 
        a bytes or bytearray stream, or a path to a file in your system.
    '''
    def read(self, f):
        data = f.read()
        data_size = len(data)
        self.mapdata_count = data_size // 2
        fb = EndianBinaryStreamReader(data)
        self.mapdata = [MapData(fb) for _ in range(self.mapdata_count)]

    def get_mapdata(self):
        return self.mapdata
    
    def set_mapdata(self, mapdata : list[MapData]):
        self.mapdata = mapdata

    def to_bytes(self) -> bytes:
        stream = EndianBinaryStreamWriter()
        for data in self.mapdata:
            data.write_to(stream)
        return stream.getvalue()