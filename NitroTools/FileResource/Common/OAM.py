from PIL import Image
from NitroTools.FileResource.Common.Tile import Tile
from NitroTools.FileResource.Common.utils import convert_from_eightbpp

class OAM:
    '''
    The OAM object represents a square, either formed by tile(s) or linear.

    :params in_data: Either a list of Tile, or a Pillow Image.Image with the right size (and P mode).
    :params size: The size of the OAM. Naturally, it must be one of those supported by the Nintendo DS.
    :params bit_depth: The bit depth of the tile data.
    :params linear: True if the data is untiled and stored linearly, False if it's tiled.
    '''
    def __init__(self, in_data : list[Tile] | Image.Image, size : tuple[int, int], pal_idx : int, bit_depth : int, linear : bool):
        assert size in VALID_OAM_SIZE, "Invalid oam size"
        self.bit_depth = bit_depth
        self.size = size
        self.width, self.height = size
        self.tile_width_count = self.width // 8
        self.tile_height_count = self.height // 8
        self.tile_count = self.tile_width_count * self.tile_height_count
        self.pal_idx = pal_idx
        self.linear = linear

        if isinstance(in_data, list):
            self.tiles = in_data
            self.image = self.build_image()

        elif isinstance(in_data, Image.Image):
            assert size == in_data.size, "Passed size and actual Image size are different"
            self.tiles = []
            for j in range(self.tile_height_count):
                for i in range(self.tile_width_count):
                    tile = Tile(in_data.crop((i * 8, j * 8, (i+1) * 8, (j+1) * 8)), self.bit_depth)            
                    self.tiles.append(tile)
            self.image = in_data

        else:
            raise Exception("Invalid input, expected bytes or Image.Image")

    def build_image(self) -> Image.Image:
        it_tiles = iter(self.tiles)
        image = Image.new(mode = 'P', size = self.size)
        if self.linear:
            data = b""
            for j in range(self.tile_height_count):
                for i in range(self.tile_width_count):
                    tile = next(it_tiles)                    
                    data += tile.to_bytes(self.pal_idx)
            image.putdata(data=data)

        else:
            for j in range(self.tile_height_count):
                for i in range(self.tile_width_count):
                    tile = next(it_tiles)                    
                    image.paste(tile.to_im(self.pal_idx), (i * 8, j * 8))

        return image
    
    def to_bytes(self) -> bytes:
        if self.linear:
            data = convert_from_eightbpp(self.image.tobytes(), self.bit_depth)
            
        else:
            data = bytearray()
            for tile in self.tiles:
                data += tile.to_bytes()

        return data
    
    def get_tiles(self):
        return self.tiles
    

VALID_OAM_SIZE = [
    (8,8), 
    (16,16), 
    (32,32), 
    (64,64), 
    (16,8), 
    (32,8), 
    (32,16), 
    (64,32), 
    (8,16), 
    (8,32), 
    (16,32), 
    (32,64)
    ]
