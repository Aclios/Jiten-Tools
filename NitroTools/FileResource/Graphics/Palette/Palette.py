from NitroTools.FileResource.File import File

class Palette(File):
    """
    The Parent Class for palette files.
    """
    def get_colors(self) -> list[int]:
        """
        Returns the palette colors.

        :returns: A list of int. Each int represents a component (Red, Green, or Blue) of a color.
            They are stored in the following way: [R1, G1, B1, R2, G2, B2, ...]. 
            That means the output has a length of 3 * number_of_color.
        """
        pass
        
    def set_colors(self, colors : list[int]):
        """
        Set the palette colors.

        :param colors: A list of int. Each int represents a component (Red, Green, or Blue) of a color.
            They must be stored in the following way: [R1, G1, B1, R2, G2, B2, ...]. 
            That means the input should have a length of 3 * number_of_color.

            WARNING: it's important to note that Nintendo DS palette colors are stored in 5 bits per
            component, meaning that imported colors might be slightly different than expected.

            For example, R = 4 would be approximated to R = 0, and R = 5 would be approximated to R = 8.

        """
        pass

    def get_bit_depth(self) -> int:
        """
        Returns the bit depth of the file (if it's defined).

        :returns: An int, the bit depth.
        """
        pass

    def set_bit_depth(self, bit_depth : int):
        """
        Set the bit depth of the file (if it's defined).

        :param bit_depth: An int, the bit depth.
        """
        pass
