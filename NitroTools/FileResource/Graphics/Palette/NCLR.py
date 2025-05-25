from NitroTools.FileSystem import EndianBinaryReader, EndianBinaryStreamWriter
from NitroTools.FileResource.Graphics.Palette.Palette import Palette
from math import ceil

class NCLR(Palette):
    '''
    Load an NCLR (for Nitro CoLor Resource) file, which contains palette data.
    It must be associated with at least an NCGR file, but may also require an additional NCER or NSCR file.

    :params inp: The input can either be an active EndianBinaryReader (if you want to read from an opened file), 
        a bytes or bytearray stream, or a path to a file in your system.
    '''
    def read(self, f : EndianBinaryReader):
        self.magic = f.check_magic(b"RLCN")
        self.unk = f.read_UInt32()
        self.filesize = f.read_UInt32()
        self.header_size = f.read_UInt16()
        self.section_count = f.read_UInt16()
        self.pltt = NCLR_PLTT(f)
        if self.section_count == 2:
            self.pcmp = NCLR_PCMP(f)

    def get_colors(self):
        if len(self.pltt.colors) > 3 * 256:
            return self.pltt.colors[0:3*256]
        else:
            return self.pltt.colors
    
    def get_bit_depth(self):
        return self.pltt.bit_depth
        
    def set_colors(self, colors : list[int]):
        if len(self.pltt.colors) > 3 * 256:
            self.pltt.colors[0 : 3 * 256] = colors
        else:
            self.pltt.colors = colors

        self.pltt.data_size = len(self.pltt.colors) // 3 * 2

        if self.section_count == 2:
            if self.pltt.bit_depth == 4:
                self.pcmp.palette_count = ceil(self.pltt.data_size / 0x20)
            elif self.pltt.bit_depth == 8:
                self.pcmp.palette_count = ceil(self.pltt.data_size / 0x200)
    
    def set_bit_depth(self, bit_depth : int):
        assert bit_depth in [4, 8], "NCLR bit depth should be either 4 or 8"
        self.pltt.bit_depth = bit_depth
        if bit_depth == 4:
            self.pltt.bit_depth_val = 3
        elif bit_depth == 8:
            self.pltt.bit_depth_val = 4

    def to_bytes(self):
        stream = EndianBinaryStreamWriter()
        stream.write(self.magic)
        stream.write_UInt32(self.unk)
        stream.write_UInt32(0)
        stream.write_UInt16(self.header_size)
        stream.write_UInt16(self.section_count)
        stream.write(self.pltt.to_bytes())

        if self.section_count == 2:
            stream.write(self.pcmp.to_bytes())

        self.filesize = stream.tell()
        stream.seek(8)
        stream.write_UInt32(self.filesize)

        return stream.getvalue()

class NCLR_PLTT:
    '''
    NCLR mandatory section, for PaLeTTe. It contains all the colors.
    '''
    def __init__(self,f : EndianBinaryReader):
        self.magic = f.check_magic(b"TTLP")
        self.section_size = f.read_UInt32()
        self.bit_depth_val = f.read_UInt16()
        if self.bit_depth_val == 3:
            self.bit_depth = 4
        elif self.bit_depth_val == 4:
            self.bit_depth = 8
        self.unk1 = f.read_UInt16()
        self.unk2 = f.read_UInt32()
        self.data_size = f.read_UInt32()
        self.data_offset = f.read_UInt32()
        self.colors = []
        for _ in range(self.data_size // 2):
            self.colors += f.read_palette_color()

    def to_bytes(self):
        stream = EndianBinaryStreamWriter()
        stream.write(self.magic)
        stream.write_UInt32(0)
        stream.write_UInt16(self.bit_depth_val)
        stream.write_UInt16(self.unk1)
        stream.write_UInt32(self.unk2)
        stream.write_UInt32(self.data_size)
        stream.write_UInt32(self.data_offset)
        for i in range(len(self.colors) // 3):
            stream.write_palette_color(self.colors[3 * i : 3 * i + 3])

        self.section_size = stream.tell()
        stream.seek(4)
        stream.write_UInt32(self.section_size)

        return stream.getvalue()

class NCLR_PCMP:
    '''
    NCLR optional section, for Palette CoMPonent. If the NCLR file contains several palettes, it gives the number of palettes and their indexes.
    '''
    def __init__(self, f : EndianBinaryReader):
        self.magic = f.check_magic(b"PMCP")
        self.section_size = f.read_UInt32()
        self.palette_count = f.read_UInt16()
        self.constant1 = f.read_UInt16()
        self.constant2 = f.read_UInt32()
        self.palettes_indexes = [f.read_UInt16() for _ in range(self.palette_count)]

    def to_bytes(self):
        stream = EndianBinaryStreamWriter()
        stream.write(self.magic)
        stream.write_UInt32(0)
        stream.write_UInt16(self.palette_count)
        stream.write_UInt16(self.constant1)
        stream.write_UInt32(self.constant2)
        for idx in self.palettes_indexes:
            stream.write_UInt16(idx)

        self.section_size = stream.tell()
        stream.seek(4)
        stream.write_UInt32(self.section_size)

        return stream.getvalue()
