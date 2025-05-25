from NitroTools.FileSystem import EndianBinaryReader, EndianBinaryStreamWriter
from NitroTools.FileResource.Common import Tile, OAM
import struct
import json
from NitroTools.FileResource.File import File

class NCER(File):
    '''
    Load an NCER (for Nitro CEll Resource) file, which contains frames data of an animation.
    Associated with an NCGR and an NCLR files, it creates several frames that are rendered by an NANR file.

    :params inp: The input can either be an active EndianBinaryReader (if you want to read from an opened file), 
        a bytes or bytearray stream, or a path to a file in your system.
    '''
    def read(self, f):
        self.magic = f.check_magic(b"RECN")
        self.unk = f.read_UInt32()
        self.filesize = f.read_UInt32()
        self.header_size = f.read_UInt16()
        self.section_count = f.read_UInt16()
        self.cebk = NCER_CEBK(f)

        if self.section_count >= 2:
            self.labl = NCER_LABL(f, self.cebk.cell_count)

        if self.section_count >= 3:
            self.uext = NCER_UEXT(f)

    def to_bytes(self):
        stream = EndianBinaryStreamWriter()
        stream.write(self.magic)
        stream.write_UInt32(self.unk)
        stream.write_UInt32(0)
        stream.write_UInt16(self.header_size)
        stream.write_UInt16(self.section_count)
        stream.write(self.cebk.to_bytes())

        if self.section_count >= 2:
            stream.write(self.labl.to_bytes())

        if self.section_count >= 3:
            stream.write(self.uext.to_bytes())

        self.filesize = stream.tell()
        stream.seek(8)
        stream.write_UInt32(self.filesize)

        return stream.getvalue()

class NCER_CEBK:
    '''
    NCER mandatory section, for CEll BanK. Contains the data to create the different cells/frames.
    '''
    def __init__(self, f : EndianBinaryReader):
        pos = f.tell()
        self.magic = f.check_magic(b"KBEC")
        self.section_size = f.read_UInt32()
        self.cell_count = f.read_UInt16()
        self.extended_flag = f.read_UInt16()
        self.data_offset = f.read_UInt32()
        flags = f.read_UInt32()
        self.tile_index_offset = (flags & 0b11) << 1
        self.sub_image_flag = flags >> 2 & 1
        self.partition_data_offset = f.read_UInt32()
        f.read(8)

        self.cells = [CEBK_Cell(f, self.extended_flag) for _ in range(self.cell_count)]
        for cell in self.cells:
            cell.read_OAM_data(f)

        if self.partition_data_offset:
            self.partition_start = f.read_UInt32()
            self.partition_size = f.read_UInt32()
            
        f.seek(pos + self.section_size)

    def to_json(self, json_filepath : str):
        cells_json = []
        for cell in self.cells:
            oams = []
            for oam in cell.OAM_data_list:
                oams.append({
                    "Color depth" : oam.color_depth,
                    "Mosaic" : oam.mosaic_flag,
                    "Obj mode" : oam.obj_mode,
                    "Obj flag" : oam.obj_flag,
                    "rot_scale_flag" : oam.rot_scale_flag,
                    "Vertical flip" : oam.ver_flip,
                    "Horizontal flip" : oam.hor_flip,
                    "Position" : [oam.x_pos, oam.y_pos],
                    "Size" : oam.size,
                    "Palette index" : oam.pal_idx,
                    "Priority" : oam.priority,
                    "Tile index" : oam.tile_index
                })
            cells_json.append(oams)
        out = {"banks" : cells_json}
        json.dump(out, open(json_filepath, mode='w', encoding='utf-8', newline=''), indent=3)

    def to_bytes(self):
        stream = EndianBinaryStreamWriter()
        stream.write(self.magic)
        stream.write_UInt32(0)
        stream.write_UInt16(self.cell_count)
        stream.write_UInt16(self.extended_flag)
        stream.write_UInt32(self.data_offset)
        stream.write_UInt32((self.tile_index_offset >> 1) + (self.sub_image_flag << 2))
        stream.write_UInt32(self.partition_data_offset)
        stream.write(bytes(8))

        data_offset = 0
        for cell in self.cells:
            stream.write_UInt16(cell.OAM_count)
            stream.write_UInt16(cell.unk)
            stream.write_UInt32(data_offset)
            if self.extended_flag:
                stream.write_Int16(cell.xmax)
                stream.write_Int16(cell.ymax)
                stream.write_Int16(cell.xmin)
                stream.write_Int16(cell.ymin)
            data_offset += cell.OAM_count * 6

        for cell in self.cells:
            for oam in cell.OAM_data_list:
                stream.write(oam.to_bytes())

        if self.partition_data_offset:
            stream.write_UInt32(self.partition_start)
            stream.write_UInt32(self.partition_size)

        self.section_size = stream.tell()
        stream.seek(4)
        stream.write_UInt32(self.section_size)

        return stream.getvalue()

class CEBK_Cell:
    '''
    A CEBK Cell (Animation frame)
    '''
    def __init__(self,f : EndianBinaryReader, extended_flag : bool):
        self.extended_flag = extended_flag
        self.OAM_count = f.read_UInt16()
        self.unk = f.read_UInt16()
        self.OAM_offset = f.read_UInt32()
        if self.extended_flag:
            self.xmax = f.read_Int16()
            self.ymax = f.read_Int16()
            self.xmin = f.read_Int16()
            self.ymin = f.read_Int16()

    def read_OAM_data(self,f : EndianBinaryReader):
        self.OAM_data_list = [OAMData(f) for _ in range(self.OAM_count)]

class OAMData:
    '''
    An NCER OAM data.
    '''
    def __init__(self, f : EndianBinaryReader):
        chunk0 = f.read_UInt16()
        self.size_type = chunk0 >> 14
        self.color_depth = chunk0 >> 13 & 1
        self.mosaic_flag = chunk0 >> 12 & 1
        self.obj_mode = chunk0 >> 10 & 0b11
        self.obj_flag = chunk0 >> 9 & 1
        self.rot_scale_flag = chunk0 >> 8 & 1
        pos_bytes = struct.pack('<B', chunk0 & (2**8 - 1))
        self.y_pos = struct.unpack('<b', pos_bytes)[0]

        chunk1 = f.read_UInt16()
        self.size_info = chunk1 >> 14
        self.ver_flip = chunk1 >> 13 & 1
        self.hor_flip = chunk1 >> 12 & 1
        x_pos_val = chunk1 & (2**9 - 1)
        if x_pos_val >= 0x100:
            self.x_pos = x_pos_val - 0x200
        else:
            self.x_pos = x_pos_val

        chunk2 = f.read_UInt16()
        self.pal_idx = chunk2 >> 12
        self.priority = chunk2 >> 10 & 0b11
        self.tile_index = chunk2 & (2**10 - 1)

        self.size = OAM_SIZE_DICT[(self.size_type,self.size_info)]

    def build_oam(self, tiles : list[Tile], tile_offset_start : int):
        bit_depth = tiles[0].bit_depth
        linear = tiles[0].linear
        if bit_depth == 4:
            tile_offset = self.tile_index * tile_offset_start
        else:
            tile_offset = self.tile_index * tile_offset_start // 2
        self.oam = OAM(self.size, tiles[tile_offset:], self.pal_idx, linear)

    def to_bytes(self):
        chunk0 = (self.size_type << 14) + (self.color_depth << 13) + (self.mosaic_flag << 12) + (self.obj_mode << 10)
        chunk0 += (self.obj_flag << 9) + (self.rot_scale_flag << 8) + struct.unpack('<B', struct.pack('<b', self.y_pos))[0]

        if self.x_pos < 0:
            x_pos_val = self.x_pos + 0x200
        else:
            x_pos_val = self.x_pos

        chunk1 = (self.size_info << 14) + (self.ver_flip << 13) + (self.hor_flip << 12) + x_pos_val

        chunk2 = (self.pal_idx << 12) + (self.priority << 10) + self.tile_index

        stream = EndianBinaryStreamWriter()
        stream.write_UInt16(chunk0)
        stream.write_UInt16(chunk1)
        stream.write_UInt16(chunk2)

        return stream.getvalue()

class NCER_LABL:
    '''
    NCER optional section, for LABeL. Contains different labels, but it's (likely) one label per animation, not per cell.
    That means there is less labels than cells in the NCER, and that they are not very useful per se.
    '''
    def __init__(self,f : EndianBinaryReader, cellbank_count : int):
        pos = f.tell()
        self.cell_names_offset = []
        self.cell_names = []
        self.magic = f.check_magic(b"LBAL")
        self.section_size = f.read_UInt32()
        for _ in range(cellbank_count):
            name_offset = f.read_UInt32()
            if name_offset >= self.section_size - 8:
                f.seek(-4, 1)
                break
            else:
                self.cell_names_offset.append(name_offset)
        name_start = f.tell()
        for name_offset in self.cell_names_offset:
            f.seek(name_start + name_offset)
            self.cell_names.append(f.read_string_until_null())

        f.seek(pos + self.section_size)

    def to_bytes(self):
        stream = EndianBinaryStreamWriter()
        stream.write(self.magic)
        stream.write_UInt32(0)
        name_offset = 0
        for name in self.cell_names:
            stream.write_UInt32(name_offset)
            name_offset += (len(name) + 1)
        for name in self.cell_names:
            stream.write(name + b'\x00')
        
        self.section_size = stream.tell()
        stream.seek(4)
        stream.write_UInt32(self.section_size)

        return stream.getvalue()

class NCER_UEXT:
    '''
    NCER optional section, for U??? EXTernal. Unknown purpose.
    '''
    def __init__(self, f : EndianBinaryReader):
        self.magic = f.check_magic(b"TXEU")
        self.section_size = f.read_UInt32()
        self.unk = f.read_UInt32()

    def to_bytes(self):
        stream = EndianBinaryStreamWriter()
        stream.write(self.magic)
        stream.write_UInt32(self.section_size)
        stream.write_UInt32(self.unk)


OAM_SIZE_DICT = {
            (0,0):(8,8),
            (0,1):(16,16),
            (0,2):(32,32),
            (0,3):(64,64),
            (1,0):(16,8),
            (1,1):(32,8),
            (1,2):(32,16),
            (1,3):(64,32),
            (2,0):(8,16),
            (2,1):(8,32),
            (2,2):(16,32),
            (2,3):(32,64)
            }