from NitroTools.FileSystem import EndianBinaryReader, EndianBinaryStreamWriter
from NitroTools.FileResource.Graphics.Bitmap.Bitmap import Bitmap

class NCGR(Bitmap):
    '''
    Load an NCGR (for Nitro Character Graphic Resource) file, which contains Bitmap Data, and other info, such as image size, 
    bit depth, linear flag.
    It must be associated with at least an NCLR file, but may also require an additional NCER or NSCR file.

    :params inp: The input can either be an active EndianBinaryReader (if you want to read from an opened file), 
        a bytes or bytearray stream, or a path to a file in your system.
    '''
    def read(self, f : EndianBinaryReader):
        self.magic = f.check_magic(b"RGCN")
        self.unk = f.read_UInt32()
        self.filesize = f.read_UInt32()
        self.header_size = f.read_UInt16()
        self.section_count = f.read_UInt16()
        assert self.section_count <= 2; "Expected a number of sections <= 2"
        self.char = NCGR_CHAR(f)

        if self.section_count == 2:
            self.cpos = NCGR_CPOS(f)

    def get_data(self) -> bytes:
        return self.char.data
    
    def get_im_size(self) -> tuple[int,int]:
        if self.char.width != -1:
            return (self.char.width * 8, self.char.height * 8)
        else:
            return None
        
    def get_bit_depth(self):
        return self.char.bit_depth
    
    def get_linear_flag(self):
        return bool(self.char.linear_flag)
    
    def set_data(self, data : bytes):
        self.char.data = data
        self.char.data_size = len(data)

    def set_im_size(self, im_size : tuple[int,int]):
        if im_size is not None:
            self.char.width = im_size[0] // 8
            self.char.height = im_size[1] // 8

    def set_bit_depth(self, bit_depth : int):
        assert bit_depth in [4, 8], "NCGR bit depth should be either 4 or 8"
        self.char.bit_depth = bit_depth
        if bit_depth == 4:
            self.char.bit_depth_val = 3
        elif bit_depth == 8:
            self.char.bit_depth_val = 4

    def set_linear_flag(self, linear_flag : bool):
        self.char.linear_flag = int(linear_flag)

    def to_bytes(self):
        stream = EndianBinaryStreamWriter()
        stream.write(self.magic)
        stream.write_UInt32(self.unk)
        stream.write_UInt32(0)
        stream.write_UInt16(self.header_size)
        stream.write_UInt16(self.section_count)
        stream.write(self.char.to_bytes())

        if self.section_count == 2:
            stream.write(self.cpos.to_bytes())

        self.filesize = stream.tell()
        stream.seek(8)
        stream.write_UInt32(self.filesize)

        return stream.getvalue()

class NCGR_CHAR:
    '''
    NCGR mandatory section, for CHARacter. The CHAR section contains pretty much all the relevant data.
    '''
    def __init__(self,f : EndianBinaryReader):
        pos = f.tell()
        self.magic = f.check_magic(b"RAHC")
        self.section_size = f.read_UInt32()
        self.height = f.read_Int16()
        self.width = f.read_Int16()
        self.bit_depth_val = f.read_UInt32()
        assert self.bit_depth_val in [3,4]
        if self.bit_depth_val == 3:
            self.bit_depth = 4
        else:
            self.bit_depth = 8
        self.unk_height = f.read_Int16()
        self.unk_width = f.read_Int16()
        self.linear_flag = f.read_UInt8()
        self.partition_flag = f.read_UInt8()
        self.unk = f.read_UInt16()
        self.data_size = f.read_UInt32()
        self.data_offset = f.read_UInt32()
        f.seek(pos + self.data_offset + 8)
        self.data = f.read(self.data_size)

    def to_bytes(self):
        stream = EndianBinaryStreamWriter()
        stream.write(self.magic)
        stream.write_UInt32(0)
        stream.write_Int16(self.height)
        stream.write_Int16(self.width)
        stream.write_UInt32(self.bit_depth_val)
        stream.write_Int16(self.unk_height)
        stream.write_Int16(self.unk_width)
        stream.write_UInt8(self.linear_flag)
        stream.write_UInt8(self.partition_flag)
        stream.write_UInt16(self.unk)
        stream.write_UInt32(self.data_size)
        stream.write_UInt32(self.data_offset)
        stream.write(self.data)

        self.section_size = stream.tell()
        stream.seek(4)
        stream.write_UInt32(self.section_size)

        return stream.getvalue()

class NCGR_CPOS:
    '''
    NCGR optional section, for Character POSition (?).
    '''
    def __init__(self,f : EndianBinaryReader):
        self.magic = f.check_magic(b"SOPC")
        self.section_size = f.read_UInt32()
        self.unknown = f.read_UInt32()
        self.char_size = f.read_UInt16()
        self.char_count = f.read_UInt16()

    def to_bytes(self):
        stream = EndianBinaryStreamWriter()
        stream.write(self.magic)
        stream.write_UInt32(self.section_size)
        stream.write_UInt32(self.unknown)
        stream.write_UInt16(self.char_size)
        stream.write_UInt16(self.char_count)
        return stream.getvalue()