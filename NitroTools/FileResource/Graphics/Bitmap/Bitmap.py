from NitroTools.FileResource.File import File

class Bitmap(File):
    """
    The Parent Class for bitmap files.
    """
    data : bytes

    def get_data(self) -> bytes:
        """
        Returns the bitmap data of the file.

        :returns: A bytes stream representing the palette indexes of the pixels of the image.
        """
        pass
    
    def set_data(self, data : bytes) -> None:
        """
        Set the bitmap data of the file.

        :param data: A bytes stream representing the palette indexes of the pixels of the image.
        """
        pass
    
    def get_im_size(self) -> tuple[int, int]:
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

    def get_bit_depth(self) -> int:
        """
        Returns the bit depth of the file (if it's defined).

        :returns: An int, the bit depth.
        """
        pass
    
    def set_bit_depth(self, bit_depth : int) -> None:
        """
        Set the bit depth of the file (if it's defined).

        :param bit_depth: An int, the bit depth.
        """
        pass
    
    def get_linear_flag(self) -> bool:
        """
        Returns whether the pixels are stored linearly (ie, if the image in untiled and the pixels are stored left to right top to bottom), or not.

        :returns: A boolean: True if the pixels are stored linearly, False if they are stored in tiles.
        """
        return False
    
    def set_linear_flag(self, linear_flag : bool) -> None:
        """
        Set whether the pixels are stored linearly (ie, if the image in untiled and the pixels are stored left to right top to bottom), or not.

        :param linear_flag: True if the pixels are stored linearly, False if they are stored in tiles.
        """