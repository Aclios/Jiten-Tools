from NitroTools.FileSystem import EndianBinaryFileReader, EndianBinaryStreamWriter
from NitroTools.FileResource.Graphics import ImageCanva
from NitroTools.FileResource.Graphics import RawBitmap, RawPalette
import csv
from pathlib import Path

def export_fonts(arm9_path : str, font_path : str):
    with EndianBinaryFileReader(arm9_path) as f:
        f.seek(0x47df4)
        font1_data = f.read(128 * 864)
        f.seek(0x62ef0)
        font2_data = f.read(128 * 1520)
        f.seek(0xbf15c)
        font1_map = f.read(2*864)
        f.seek(0xd78d4)
        font2_map = f.read(2*1520)

    bitmap = RawBitmap(font1_data)
    palette = RawPalette(b"\x00\x00\x00\x00\x00\x00\xff\x7f")
    nds_im = ImageCanva(Bitmap=bitmap, Palette=palette, bit_depth=4, im_size=(256, 864))
    font1_im = nds_im.build_im()
    font1_im.save(Path(font_path) / "font1.png")

    bitmap = RawBitmap(font2_data)
    palette = RawPalette(b"\x00\x00\xff\x7f")
    nds_im = ImageCanva(Bitmap=bitmap, Palette=palette, bit_depth=4, im_size=(256, 1520))
    font2_im = nds_im.build_im()
    font2_im.save(Path(font_path) / "font2.png")

def parse_fontmap(fontmap_path : str):
    metrics = []
    characters = []
    with open(fontmap_path, encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            for data in row:
                if data == "RESERVED":
                    metrics.append(None)
                    characters.append(None)
                else:
                    char, metric = data.split("|")
                    metrics.append(metric)
                    characters.append(char)
    assert len(characters) == 256
    return metrics, characters


def import_fonts(arm9_path : str, font_dir : str):
    png_path = Path(font_dir) / "font.png"
    map_path = Path(font_dir) / "fontmap.csv"
    metrics, _ = parse_fontmap(map_path)
    nds_im = ImageCanva(Bitmap=RawBitmap(b""), Palette=RawPalette(b""), bit_depth=4, im_size=(256, 256))
    nds_im.import_image(png_path)
    font2_data = nds_im.Bitmap.to_bytes()
    font1_data = bytes()
    for val in font2_data:
        font1_data += (val * 3).to_bytes(1, 'big')
    f1 = EndianBinaryStreamWriter(endianness = 'big')
    f2 = EndianBinaryStreamWriter(endianness = 'big')
    for idx, metric in enumerate(metrics):
        if idx == 0: #0 is used as an end of data character ; using it as a character id will make weird bugs with all the changes
            f1.write_UInt16(0x8000 + idx) #doesn't matter here
            f2.write_UInt8(0x23) #0x23 is another unused id since it is used to announce codes, so we use it as a placeholder
        else:
            f1.write_UInt16(0x8000 + idx)
            f2.write_UInt8(idx)
        if metric is None:
            f1.write_UInt8(0x10)
            f2.write_UInt8(0x10)
        else:
            f1.write_UInt8(int(metric))
            f2.write_UInt8(int(metric))

    f1.write_UInt16(0)
    f2.write_UInt16(0)
    font1_map = f1.getvalue()
    font2_map = f2.getvalue()
    with open(arm9_path, mode='rb+') as f:
        f.seek(0x47DF4)
        f.write(font1_data)
        f.seek(0x62EF0)
        f.write(font2_data)
        f.seek(0xBF15C)
        f.write(font1_map)
        f.seek(0xD78D4)
        f.write(font2_map)


