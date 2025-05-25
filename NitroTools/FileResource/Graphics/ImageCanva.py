from NitroTools.FileResource.Graphics.Bitmap import *
from NitroTools.FileResource.Graphics.Palette import *
from NitroTools.FileResource.Graphics.Tilemap import *
from NitroTools.FileResource.Graphics.Cell import *
from PIL import Image
from NitroTools.FileResource.Common import Tile, OAM, paste_alpha, convert_from_eightbpp, convert_to_eightbpp, empty_im

class ImageCanva:
    def __init__(
        self,
        Bitmap : Bitmap = None,
        Palette : Palette = None,
        Tilemap : Tilemap | NSCR = None,
        Cell : NCER = None,
        bit_depth : int = None,
        im_size : tuple[int, int] = None,
        OAM_size : tuple[int, int] = (8,8),
        transparency : bool = False,
        linear : bool = False
        ):
        
        self.load_Bitmap(Bitmap)
        self.load_Palette(Palette)
        self.load_Cell(Cell)
        self.load_Tilemap(Tilemap)

        self.set_im_size(im_size)
        self.set_OAM_size(OAM_size)
        self.set_bit_depth(bit_depth)
        self.set_transparency(transparency)
        self.set_linear(linear)

    def load_Bitmap(self, Bitmap : Bitmap):
        '''
        Load a Bitmap object to the Canva, and set its parameters (bit depth, image size, linearity) if they exist.

        :params Bitmap: A Bitmap object.
        '''
        self.Bitmap = Bitmap
        if Bitmap is not None:
            self.set_bit_depth(self.Bitmap.get_bit_depth())
            self.set_im_size(self.Bitmap.get_im_size())
            self.set_linear(self.Bitmap.get_linear_flag())

    def load_Tilemap(self, Tilemap : Tilemap):
        '''
        Load a Tilemap object to the Canva, and set its parameters (image size) if they exist.

        :params Tilemap: A Tilemap object.
        '''
        self.Tilemap = Tilemap
        if Tilemap is not None:
            self.set_im_size(self.Tilemap.get_im_size())

    def load_Palette(self, Palette : Palette):
        '''
        Load a Palette object to the Canva, and set its parameters (bit depth) if they exist.

        :params Palette: A Palette object.
        '''
        self.Palette = Palette
        if Palette is not None:
            self.set_bit_depth(self.Palette.get_bit_depth())

    def load_Cell(self, Cell : NCER):
        '''
        Load a Cell object to the Canva.

        :params Cell: A NCER object.
        '''
        self.Cell = Cell

    def set_im_size(self, im_size : tuple[int, int]):
        '''
        Set the image size of the Canva. 
        
        This is only relevant if you are dealing with raw Bitmap/Palette.

        :params im_size: A tuple (width, height).
        '''
        if im_size is not None:
            self.im_size = im_size
            self.im_width, self.im_height = im_size

    def set_OAM_size(self, OAM_size : tuple[int, int]):
        '''
        Set the OAM size of the Canva. 
        
        This is only relevant if you are dealing with raw Bitmap/Palette.

        :params im_size: A tuple (OAM_width, OAM_height).
        '''
        if OAM_size is not None:
            self.OAM_size = OAM_size
            self.OAM_width, self.OAM_height = OAM_size

    def set_bit_depth(self, bit_depth : int):
        '''
        Set the bit depth of the Canva. 
        
        This is only relevant if you are dealing with raw Bitmap/Palette.

        :params bit_depth: The bit depth.
        '''
        if bit_depth in [2, 4, 8]:

            self.bit_depth = bit_depth

        elif bit_depth is None:
            pass

        else:
            raise Exception('Invalid bit depth value. Should be either 2, 4 or 8.')
        
    def set_linear(self, linear_flag : bool):
        '''
        Set the linearity of the Canva. If it's set to False, the Bitmap data will be read as tiles. If it's set to True,
        the Bitmap data will be read left/right top/bottom.

        This is only relevant if you are dealing with raw Bitmap/Palette.

        :params linear_flag: The linear flag.
        '''
        self.linear = linear_flag

    def set_transparency(self, transparency : bool):
        '''
        Set whether the index 0 of the palette indicates fully transparent pixels.

        This isn't required, since transparent pixels usually have a distinct color.

        :params transparency: Transparency flag.
        '''
        self.transparency = transparency

    def generate_tile_list(self):
        '''
        Generate tiles from the loaded Bitmap.
        '''
        tile_datasize = self.bit_depth * 8
        data = self.Bitmap.get_data()
        tile_count = len(data) // tile_datasize
        tiles = [Tile(data[tile_datasize * idx : tile_datasize * (idx + 1)], self.bit_depth) for idx in range(tile_count)]
        return tiles

    def build_hor_image(self, pal_idx : int = 0):
        '''
        Build a tiled image, by solely using a Bitmap and a Palette.

        :params pal_idx: The index of the subpalette the image should follow. It is useful if the same Bitmap has several colorings,
        for example for an animation.
        '''
        OAM_width_count = self.im_width // self.OAM_width
        OAM_height_count = self.im_height // self.OAM_height
        im = empty_im(self.im_size, self.Palette.get_colors(), self.bit_depth, self.transparency)
        tile_idx = 0
        tiles = self.generate_tile_list()
        tile_count_par_OAM = (self.OAM_width // 8) * (self.OAM_height // 8)
        for j in range(OAM_height_count):
            for i in range(OAM_width_count):
                oam = OAM(tiles[tile_idx : tile_idx + tile_count_par_OAM], self.OAM_size, pal_idx, self.bit_depth, False)
                tile_idx += tile_count_par_OAM
                im.paste(oam.image, (i * self.OAM_width, j * self.OAM_height))
        return [im]
    
    def build_linear_image(self, pal_idx : int):
        '''
        Build a linear image, by solely using a Bitmap and a Palette.

        :params pal_idx: The index of the subpalette the image should follow. It is useful if the same Bitmap has several colorings,
        for example for an animation.
        '''
        im = empty_im(self.im_size, self.Palette.get_colors(), self.bit_depth, self.transparency)
        eightbpp_data = convert_to_eightbpp(self.Bitmap.get_data(), self.bit_depth, pal_idx)
        im.putdata(eightbpp_data)
        return [im]
    
    def build_image_with_tilemap(self):
        '''
        Build an image, by using a Bitmap, a Palette, and a Tilemap.
        '''
        im = empty_im(self.im_size, self.Palette.get_colors(), self.bit_depth, self.transparency)
        tiles = self.generate_tile_list()
        maps = iter(self.Tilemap.get_mapdata())
        for j in range(im.height // 8):
            for i in range(im.width // 8):
                map = next(maps)
                tile_im = map.get_tile_im(tiles)
                im.paste(tile_im, (i * 8, j * 8))
        return [im]
    
    def build_cells(self):
        '''
        Build the different frames defined by a Cell, using a Bitmap and a Palette.
        '''
        tiles = self.generate_tile_list()
        cell_images = []
        for cell_bank in self.Cell.cebk.cells:
            if len(cell_bank.OAM_data_list) == 0:
                cell_images.append(None)
                continue

            min_x = min([OAM_data.x_pos for OAM_data in cell_bank.OAM_data_list])
            min_y = min([OAM_data.y_pos for OAM_data in cell_bank.OAM_data_list])
            max_x = max([OAM_data.x_pos + OAM_data.size[0] for OAM_data in cell_bank.OAM_data_list])
            max_y = max([OAM_data.y_pos + OAM_data.size[1] for OAM_data in cell_bank.OAM_data_list])
            cell_im_size = (max_x - min_x, max_y - min_y)
            cell_im = empty_im(cell_im_size, self.Palette.get_colors(), self.bit_depth, True)

            if self.bit_depth == 4:
                transparency_idx = [i * 16 for i in range(16)]
            else:
                transparency_idx = [0]
            
            for OAM_data in cell_bank.OAM_data_list[::-1]:
                if self.bit_depth == 4:
                    tile_offset = OAM_data.tile_index * self.Cell.cebk.tile_index_offset
                else:
                    tile_offset = OAM_data.tile_index * self.Cell.cebk.tile_index_offset // 2

                oam = OAM(tiles[tile_offset:], OAM_data.size, OAM_data.pal_idx, self.bit_depth, self.linear)
                OAM_im = oam.image
                if OAM_data.ver_flip:
                    OAM_im = OAM_im.transpose(Image.FLIP_TOP_BOTTOM)
                if OAM_data.hor_flip:
                    OAM_im = OAM_im.transpose(Image.FLIP_LEFT_RIGHT)

                cell_im = paste_alpha(cell_im, OAM_im, (OAM_data.x_pos - min_x, OAM_data.y_pos - min_y), transparency_idx)
            cell_images.append(cell_im)

        return cell_images
        
    def build_im(self, pal_idx : int = 0):
        '''
        Build automatically the image(s) using the objects currently loaded in th Canva.

        :params pal_idx: The index of the subpalette the image should follow. It is useful if the same Bitmap has several colorings,
        for example for an animation. It isn't used if there is a Tilemap or a Cell object.
        '''
        assert self.Bitmap is not None and self.Palette is not None, "At least a palette and a bitmap are required"
        if self.Cell is not None:
            return self.build_cells()
        elif self.Tilemap is not None:
            return self.build_image_with_tilemap()
        else:
            if not self.linear:
                return self.build_hor_image(pal_idx)
            else:
                return self.build_linear_image(pal_idx)

    def import_image(self, im_filepath : str, cell_idx : int = 0):
        im = Image.open(im_filepath)
        assert im.mode == "P", "Invalid png type, pyNitro is expecting a color indexed png."  
        assert self.Bitmap is not None and self.Palette is not None, "At least a palette and a bitmap are required"
        if self.Cell is not None:
            self.import_cell(im, cell_idx)
        elif self.Tilemap is not None:
            self.import_image_with_tilemap(im)
        else:
            if not self.linear:
                self.import_hor_image(im)
            else:
                self.import_linear_image(im)
            
    def import_cell(self, im : Image.Image, cell_idx : int):
        '''
        Import an image to a cell.

        :params im: The Image.
        :params cell_idx: The cell index.
        '''
        colors = im.getpalette()
        self.tiles = self.generate_tile_list()
        cell = self.Cell.cebk.cells[cell_idx]
        min_x = min([OAM_data.x_pos for OAM_data in cell.OAM_data_list])
        min_y = min([OAM_data.y_pos for OAM_data in cell.OAM_data_list])

        for OAM_data in cell.OAM_data_list:
            oam = OAM(im.crop((OAM_data.x_pos - min_x, OAM_data.y_pos - min_y, OAM_data.x_pos + OAM_data.oam.width - min_x, OAM_data.y_pos + OAM_data.oam.height - min_y)), OAM_data.size, OAM_data.pal_idx, self.bit_depth, self.linear)
            new_tiles = OAM.get_tiles()

            if self.bit_depth == 4:
                tile_offset = OAM_data.tile_index * self.Cell.cebk.tile_index_offset
            else:
                tile_offset = OAM_data.tile_index * self.Cell.cebk.tile_index_offset // 2

            self.tiles[tile_offset : tile_offset + oam.tile_count] = new_tiles

        newdata = bytearray()
        for tile in self.tiles:
            newdata += tile.to_bytes()

        self.Bitmap.set_data(newdata)
        self.Palette.set_colors(colors)

    def import_image_with_tilemap(self, im : Image.Image):
        '''
        Import an image that use a tilemap.

        :params im: The Image.
        '''
        colors = im.getpalette()
        mapinfos : list[MapData] = []
        data = bytes()
        tiles_data : list[bytes] = []
        for j in range(im.height // 8):
            for i in range(im.width // 8):
                tile_data = im.crop((i * 8, j * 8, (i+1) * 8, (j+1) * 8)).tobytes()
                if self.bit_depth == 8:
                    pal_idx = 0
                elif self.bit_depth == 4:
                    pal_idx = tile_data[0] // 0x10
                elif self.bit_depth == 2:
                    pal_idx = tile_data[0] // 0x4
                tile_data = convert_from_eightbpp(tile_data, self.bit_depth)
                if tile_data in tiles_data:
                    tile_idx = tiles_data.index(tile_data)
                else:
                    tiles_data.append(tile_data)
                    data += tile_data
                    tile_idx = len(tiles_data) - 1
                mapdata = MapData()
                mapdata.tile_idx = tile_idx
                mapdata.pal_idx = pal_idx
                mapinfos.append(mapdata)

        self.Bitmap.set_data(data)
        self.Palette.set_colors(colors)
        self.Tilemap.set_mapdata(mapinfos)
        self.Tilemap.set_im_size(im.size)

    def import_hor_image(self, im : Image.Image):
        '''
        Import an tiled image that only use a bitmap and a palette.

        :params im: The Image.
        '''
        colors = im.getpalette()
        data = bytearray()
        for j in range(im.height // self.OAM_height):
            for i in range(im.width // self.OAM_width):
                oam = OAM(im.crop((i * self.OAM_width, j * self.OAM_height, (i+1) * self.OAM_width, (j+1) * self.OAM_height)), self.OAM_size, 0, self.bit_depth, False)
                data += oam.to_bytes()
        self.Bitmap.set_data(data)
        self.Bitmap.set_im_size(im.size)
        self.Palette.set_colors(colors)
        
    def import_linear_image(self, im : Image.Image):
        '''
        Import an linear image that only use a bitmap and a palette.

        :params im: The Image.
        '''
        colors = im.getpalette()
        data = convert_from_eightbpp(im.tobytes(), self.bit_depth)
        self.Bitmap.set_data(data)
        self.Bitmap.set_im_size(im.size)
        self.Palette.set_colors(colors)