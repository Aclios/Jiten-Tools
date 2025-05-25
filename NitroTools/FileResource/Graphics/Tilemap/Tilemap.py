from NitroTools.FileResource.File import File
from NitroTools.FileSystem import EndianBinaryReader, EndianBinaryWriter
from NitroTools.FileResource.Common import Tile
from PIL import Image

class MapData:
    '''
    The MapData object contains the info of a tile of a mapped image: tile index, palette index, and rotation flags.
    '''
    def __init__(self, f : EndianBinaryReader = None):
        self.flip_top_bottom = False
        self.flip_left_right = False
        if f is not None:
            data = f.read_UInt16()
            self.pal_idx = data // 0x1000
            data -= self.pal_idx * 0x1000
            if data >= 0x800:
                data -= 0x800
                self.flip_top_bottom = True
            if data >= 0x400:
                data -= 0x400
                self.flip_left_right = True
            self.tile_idx = data

    def write_to(self, f : EndianBinaryWriter) -> None:
        '''
        Writes the MapInfo data to the stream f.
        '''
        data = self.pal_idx * 0x1000
        if self.flip_top_bottom:
            data += 0x800
        if self.flip_left_right:
            data += 0x400
        data += self.tile_idx
        f.write_UInt16(data)

    def get_tile_im(self, tiles : list[Tile]):
        '''
        Returns a PIL Image representing the tile defined by this.

        :param tiles: A list of Tiles, generated from the Bitmap file associated to the Tilemap file.

        :returns: A 8x8 PIL Image representing the tile.
        '''
        tile_im = tiles[self.tile_idx].to_im(self.pal_idx)
        if self.flip_top_bottom:
            tile_im = tile_im.transpose(Image.FLIP_TOP_BOTTOM)
        if self.flip_left_right:
            tile_im = tile_im.transpose(Image.FLIP_LEFT_RIGHT)
        return tile_im

class Tilemap(File):
    """
    The Parent Class for tilemap files.
    """
    def get_mapdata(self) -> list[MapData]:
        '''
        Returns tile mapping data.

        :returns: A list of MapData objects.
        '''
        pass
    
    def set_mapdata(self, mapdata : list[MapData]):
        '''
        Set tile mapping data.

        :params mapdata: A list of MapData objects.
        '''
        pass

    def get_im_size(self) -> tuple[int,int]:
        """
        Returns the image size of the file (if it's defined).

        :returns: A tuple (width, height).
        """
        pass
    
    def set_im_size(self, im_size : tuple[int, int]):
        """
        Set the image size of the file (if it's defined).

        :param im_size: A tuple (width, height).
        """
        pass