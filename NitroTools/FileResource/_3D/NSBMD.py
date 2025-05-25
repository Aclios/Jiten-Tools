from NitroTools.FileSystem import EndianBinaryReader
from NitroTools.FileResource.File import File
from NitroTools.FileResource.Graphics import ImageCanva, RawBitmap, RawPalette
from NitroTools.FileResource.Common import texel_decompress

from pathlib import Path
import os

class NSBMD(File):
    def read(self, f : EndianBinaryReader):
        self.magic = f.check_magic(b'BMD0')
        self.unk = f.read_UInt32()
        self.filesize = f.read_UInt32()
        self.header_size = f.read_UInt16()
        self.section_count = f.read_UInt16()
        assert self.section_count <= 2, f"Unsupported section count for NSBMD: {self.section_count}, expected 2 or less"
        self.mdl_offset = f.read_UInt32()
        if self.section_count == 2:
            self.tex_offset = f.read_UInt32()
        f.seek(self.mdl_offset)
        self.mdl = MDL0(f)
        if self.section_count == 2:
            f.seek(self.tex_offset)
            self.tex = TEX0(f)

    def export_textures(self, out_dir : str):
        self.tex.export_textures(out_dir)

class MDL0:
    def __init__(self, f : EndianBinaryReader):
        self.magic = f.check_magic(b'MDL0')
        self.section_size = f.read_UInt32()
        self.data = f.read(self.section_size - 8)

class TEX0:
    def __init__(self, f : EndianBinaryReader):
        self.offset = f.tell()
        self.magic = f.check_magic(b'TEX0')
        self.section_size = f.read_UInt32()
        self.padding1 = f.read_UInt32()
        self.tex_region_size = f.read_UInt16()
        self.tex_info_offset = f.read_UInt16()
        self.padding2 = f.read_UInt32()
        self.tex_data_offset = f.read_UInt32()
        self.padding3 = f.read_UInt32()
        self.tex_compressed_region_size = f.read_UInt16() << 3
        self.tex_compressed_info_offset = f.read_UInt16()
        self.padding4 = f.read_UInt32()
        self.tex_compressed_data_offset = f.read_UInt32()
        self.tex_compressed_info_data_offset = f.read_UInt32()
        self.padding5 = f.read_UInt32()
        self.palette_data_size = f.read_UInt32() << 3
        self.palette_info_offset = f.read_UInt32()
        self.palette_data_offset = f.read_UInt32()

        f.seek(self.offset + self.tex_info_offset)
        self.tex_info = TexInfo(f)

        f.seek(self.offset + self.palette_info_offset)
        self.pal_info = PaletteInfo(f)

        for idx, _ in enumerate(self.tex_info.parameters):
            self.tex_info.parameters[idx].bitmap_data, self.tex_info.parameters[idx].palette_data, self.tex_info.parameters[idx].compression_info_data = self.get_texture(f, idx)

    def export_textures(self, out_dir : str):
        os.makedirs(out_dir, exist_ok = True)
        for idx in range(len(self.tex_info.parameters)):
            name = self.tex_info.names[idx]
            im = self.tex_info.parameters[idx].build_image()
            im.save(Path(out_dir) / (name.decode() + '.png'))

    def get_texture(self, f : EndianBinaryReader, tex_idx : int):
        assert tex_idx < len(self.tex_info.parameters), f"Given idx ({tex_idx}) is beyond max tex idx ({len(self.tex_info.parameters)})"
        if self.tex_info.parameters[tex_idx].format != 5:
            bitmap_offset = self.tex_info.parameters[tex_idx].tex_offset * 8 + self.offset + self.tex_data_offset
            f.seek(bitmap_offset)
            bitmap_data =  f.read(self.tex_info.parameters[tex_idx].width * self.tex_info.parameters[tex_idx].height * self.tex_info.parameters[tex_idx].bit_depth // 8)
        else:
            bitmap_offset = self.tex_info.parameters[tex_idx].tex_offset * 8 + self.offset + self.tex_compressed_data_offset
            f.seek(bitmap_offset)
            bitmap_data =  f.read(self.tex_info.parameters[tex_idx].width * self.tex_info.parameters[tex_idx].height // 4)

        palette_offset = self.offset + self.palette_data_offset + self.pal_info.parameters[tex_idx].pal_offset * 8

        f.seek(palette_offset)
        palette_data = f.read(FORMAT_PALETTE_SIZE[self.tex_info.parameters[tex_idx].format])

        if self.tex_info.parameters[tex_idx].format == 5:
            compression_info_offset = self.offset + self.tex_compressed_info_data_offset + self.find_compression_info_offset(tex_idx)
            f.seek(compression_info_offset)
            info_data = f.read(self.tex_info.parameters[tex_idx].width * self.tex_info.parameters[tex_idx].height // 8)
        else:
            info_data = bytes()
        
        return bitmap_data, palette_data, info_data
             
    def find_compression_info_offset(self, tex_idx : int):
        compression_info_offset = 0
        for parameters in self.tex_info.parameters[0 : tex_idx]:
            if parameters.format == 5:
                compression_info_offset += (parameters.width + parameters.height // 8)
        return compression_info_offset


class TexInfo:
    def __init__(self, f : EndianBinaryReader):
        self.unk = f.read_UInt8()
        self.tex_count = f.read_UInt8()
        self.section_size = f.read_UInt16()

        self.unk_header_size = f.read_UInt16() #8
        self.unk_section_size = f.read_UInt16()
        self.constant = f.read_UInt32()
        self.unk1 = [f.read_UInt16() for _ in range(self.tex_count)]
        self.unk2 = [f.read_UInt16() for _ in range(self.tex_count)]

        self.info_header_size = f.read_UInt16() #8? Should be 4?
        self.info_section_size = f.read_UInt16()
        self.parameters = [TexParameters(f) for _ in range(self.tex_count)]

        self.names = [f.read(0x10).strip(b'\x00') for _ in range(self.tex_count)]

class TexParameters:
    bitmap_data : bytes
    palette_data : bytes
    compression_info_data : bytes
    def __init__(self, f : EndianBinaryReader):
        self.tex_offset = f.read_UInt16()
        self.parameters = f.read_UInt16()
        self.width2 = f.read_UInt8()
        self.unk1 = f.read_UInt8()
        self.unk2 = f.read_UInt8()
        self.unk3 = f.read_UInt8()

        self.coord_transform = self.parameters & 14
        self.color = (self.parameters >> 13) & 1
        self.format = (self.parameters >> 10) & 7
        self.height = 8 << ((self.parameters >> 7) & 7)
        self.width = 8 << ((self.parameters >> 4) & 7)
        self.flip_y = (self.parameters >> 3) & 1
        self.flip_x = (self.parameters >> 2) & 1
        self.repeat_y = (self.parameters >> 1) & 1
        self.repeat_x = self.parameters & 1

        if self.width == 0:
            if self.unk1 & 3 == 2:
                self.width = 0x200
            else:
                self.width = 0x100

        if self.height == 0:
            if (self.unk1 >> 4) & 3  == 2:
                self.height = 0x200
            else:
                self.height = 0x100

        self.bit_depth = FORMAT_BITDEPTH[self.format]

    def build_image(self):
        if self.format == 5:
            data, calculated_palette = texel_decompress(self.bitmap_data, self.compression_info_data, RawPalette(self.palette_data), (self.width, self.height))
            bitmap = RawBitmap(data)
            palette = RawPalette(calculated_palette)
        else:
            bitmap = RawBitmap(self.bitmap_data)
            palette = RawPalette(self.palette_data)

        im = ImageCanva(Bitmap = bitmap, Palette=palette, bit_depth = self.bit_depth, im_size = (self.width, self.height), linear=True)
        return im.build_im()[0]


class PaletteInfo:
    def __init__(self, f : EndianBinaryReader):
        self.unk = f.read_UInt8()
        self.pal_count = f.read_UInt8()
        self.section_size = f.read_UInt16()

        self.unk_header_size = f.read_UInt16() #8
        self.unk_section_size = f.read_UInt16()
        self.constant = f.read_UInt32()
        self.unk1 = [f.read_UInt16() for _ in range(self.pal_count)]
        self.unk2 = [f.read_UInt16() for _ in range(self.pal_count)]

        self.info_header_size = f.read_UInt16() #8
        self.info_section_size = f.read_UInt16()
        self.parameters = [PaletteParameters(f) for _ in range(self.pal_count)]

        self.names = [f.read(0x10).strip(b'\x00') for _ in range(self.pal_count)]

class PaletteParameters:
    def __init__(self, f : EndianBinaryReader):
        self.pal_offset = f.read_UInt16() & 0x1FFF
        self.padding = f.read_UInt16()

FORMAT_PALETTE_SIZE = {
    0 : 0,
    1 : 0x40,
    2 : 0x8,
    3 : 0x20,
    4 : 0x200,
    5 : 0x200,
    6 : 0x10,
    7 : 0
    }

FORMAT_BITDEPTH = {
    0 : 0,
    1 : 8,
    2 : 2,
    3 : 4,
    4 : 8,
    5 : 8, #compressed
    6 : 8,
    7 : 16
    }