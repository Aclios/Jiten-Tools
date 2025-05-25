from NitroTools.FileSystem import EndianBinaryReader, EndianBinaryStreamWriter
from NitroTools.FileResource.Graphics.Tilemap.Tilemap import Tilemap, MapData

class NSCR(Tilemap):
    '''
    Load an NSCR (for Nitro SCreen Resource) file, which contains tile mapping data.
    It must be associated with an NCGR and an NCLR files, and it forms an image, generally a background.

    :params inp: The input can either be an active EndianBinaryReader (if you want to read from an opened file), 
        a bytes or bytearray stream, or a path to a file in your system.
    '''
    def read(self, f : EndianBinaryReader):
        self.magic = f.check_magic(b"RCSN")
        self.unk = f.read_UInt32()
        self.filesize = f.read_UInt32()
        self.header_size = f.read_UInt16()
        self.section_count = f.read_UInt16()
        assert self.section_count == 1
        self.scrn = NSCR_SCRN(f)

    def get_mapdata(self) -> list[MapData]:
        return self.scrn.mapdata
    
    def get_im_size(self) -> tuple[int,int]:
        return (self.scrn.im_width, self.scrn.im_height)
    
    def set_mapdata(self, mapdata : list):
        self.scrn.mapdata = mapdata
        self.scrn.mapdata_size = len(mapdata) * 2

    def set_im_size(self, im_size : tuple[int, int]):
        self.scrn.im_width, self.scrn.im_height = im_size
    
    def to_bytes(self):
        stream = EndianBinaryStreamWriter()
        stream.write(self.magic)
        stream.write_UInt32(self.unk)
        stream.write_UInt32(0)
        stream.write_UInt16(self.header_size)
        stream.write_UInt16(self.section_count)
        stream.write(self.scrn.to_bytes())

        self.filesize = stream.tell()
        stream.seek(8)
        stream.write_UInt32(self.filesize)

class NSCR_SCRN:
    '''
    NSCR mandatory (and only) section. Contains the map data, and the dimensions of the image.
    '''
    def __init__(self, f : EndianBinaryReader):
        self.magic = f.check_magic(b"NRCS")
        self.section_size = f.read_UInt32()
        self.im_width = f.read_UInt16()
        self.im_height = f.read_UInt16()
        self.unk = f.read_UInt32()
        self.mapdata_size = f.read_UInt32()
        self.mapdata = [MapData(f) for _ in range(self.mapdata_size // 2)]

    def to_bytes(self):
        stream = EndianBinaryStreamWriter()
        stream.write(self.magic)
        stream.write_UInt32(0)
        stream.write_UInt16(self.im_width)
        stream.write_UInt16(self.im_height)
        stream.write_UInt32(self.unk)
        stream.write_UInt32(self.mapdata_size)
        for data in self.mapdata:
            data.write_to(stream)

        self.section_size = stream.tell()
        stream.seek(4)
        stream.write_UInt32(self.section_size)

        return stream.getvalue()