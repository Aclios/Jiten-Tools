from PIL import Image
from NitroTools.FileResource.Common.utils import convert_from_eightbpp, convert_to_eightbpp

class Tile:
    '''
    The Tile object represents a 8x8 pixel tile.

    :params in_data: Either bytes (a bitmap stream), or an 8x8 Pillow Image.Image (with P mode).
    :params bit_depth: The bit depth of the tile data.
    '''
    def __init__(self, in_data : bytes | Image.Image, bit_depth : int):
        self.bit_depth = bit_depth

        if isinstance(in_data, bytes):
            assert len(in_data) == EXPECTED_DATA_SIZE[self.bit_depth], "Invalid data size"
            self.data = in_data

        elif isinstance(in_data, Image.Image):
            assert in_data.size == (8,8), "Image dimensions should be 8,8"
            self.data = convert_from_eightbpp(in_data.tobytes(), self.bit_depth)

        else:
            raise Exception("Invalid input, expected bytes or Image.Image")
        
    def to_bytes(self):
        '''
        Returns the bitmap data of this tile.
        '''
        return self.data
        
    def to_im(self, pal_idx : int) -> Image.Image:
        '''
        Creates an Image representing this tile. This Image doesn't have a palette, 
        so it must be pasted to another Image with a palette to be viewed.

        :params pal_idx: Push the pixels to the given palette index.
        '''
        return Image.frombytes(mode = 'P', size = (8,8), data = convert_to_eightbpp(self.data, self.bit_depth, pal_idx))  
    
EXPECTED_DATA_SIZE = {
    8 : 64,
    4 : 32,
    2 : 16,
    1 : 8
}