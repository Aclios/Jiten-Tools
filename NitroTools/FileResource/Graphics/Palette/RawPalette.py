from NitroTools.FileSystem import EndianBinaryReader, EndianBinaryStreamWriter
from NitroTools.FileResource.Graphics.Palette.Palette import Palette

class RawPalette(Palette):
    '''
    Load a raw palette. It must be associated with at least a RawBitmap, and may require a RawTilemap.

    .. warning::
        If you pass an EndianBinaryReader, it will use all the data until the end of the file; if you pass a path,
        it will use the entirety of the data of the file. Read the file yourself and pass bytes/bytearray if this
        behavior is a problem.

    :params inp: The input can either be an active EndianBinaryReader (if you want to read from an opened file), 
        a bytes or bytearray stream, or a path to a file in your system.
    '''
    def read(self, f : EndianBinaryReader):
        f.seek(0, 2)
        self.color_count = f.tell() // 2
        f.seek(0)
        self.colors = []
        for _ in range(self.color_count):
            self.colors.extend(f.read_palette_color())

    def get_colors(self):
        if len(self.colors) > 3 * 256: #indexed png only handle up to 256 colors, so we can't push more than that. Bigger palettes (typically 8bpp with several full palettes) can't be fully exported 
            return self.colors[0:3*256]
        else:
            return self.colors
        
    def set_colors(self, colors : list[int]):
        if len(self.colors) > 3 * 256:
            self.colors[0:3 * 256] = colors
        else:
            self.colors = colors

    def to_bytes(self):
        f = EndianBinaryStreamWriter()
        for i in range(len(self.colors) // 3):
            f.write_palette_color(self.colors[3 * i : 3 * i + 3])
        return f.getvalue()

