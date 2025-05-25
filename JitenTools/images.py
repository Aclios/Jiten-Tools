from NitroTools.FileResource.Graphics import RawBitmap, RawPalette, RawTilemap, ImageCanva
import csv
from pathlib import Path

def export_images(databin_dir : str, extract_dir : str, filemap_path : str):
    with open(filemap_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        verify_unicity = []
        for row in reader:
            if row[0] == 'bitmap_idx':
                continue
            bitmap_idx, palette_idx, bpp, tilemap_idx, linear, im_width, im_height, OAM_width, OAM_height, alpha, filepath = row[0:11]
            Bitmap = Palette = Tilemap = None
            if bitmap_idx:
                Bitmap = RawBitmap(Path(databin_dir, f'{int(bitmap_idx):04d}.{bpp}bpp'))
            if palette_idx:
                Palette = RawPalette(Path(databin_dir, f'{int(palette_idx):04d}.ndspal'))
            if tilemap_idx:
                Tilemap = RawTilemap(Path(databin_dir, f'{int(tilemap_idx):04d}.tilemap'))
            
            if filepath in verify_unicity: raise Exception(filepath)
            verify_unicity.append(filepath)

            linear_flag = (linear != '')
            if OAM_width: OAM_width = int(OAM_width)
            if OAM_height: OAM_height = int(OAM_height)

            canva = ImageCanva(Bitmap=Bitmap, Palette=Palette, Tilemap=Tilemap,
                               bit_depth=int(bpp), im_size=(int(im_width), int(im_height)),
                               OAM_size=(OAM_width, OAM_height), linear=linear_flag)
            
            image = canva.build_im()[0]

            out_path = Path(extract_dir, filepath + '.png')
            out_path.parent.mkdir(parents= True, exist_ok = True)
            print(f'Export {out_path}')

            image.save(out_path)


def import_images(databin_dir : str, png_dir : str, filemap_path : str, new_databin_dir : str):
    with open(filemap_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0] == 'bitmap_idx':
                continue
            bitmap_idx, palette_idx, bpp, tilemap_idx, linear, im_width, im_height, OAM_width, OAM_height, alpha, filepath = row[0:11]
            png_path = Path(png_dir, filepath + '.png')
            if png_path.exists():
                print(f'Importing {filepath}...')

                Bitmap = RawBitmap(Path(databin_dir, f'{int(bitmap_idx):04d}.{bpp}bpp'))
                Palette = RawPalette(Path(databin_dir, f'{int(palette_idx):04d}.ndspal'))
                Tilemap = None
                if tilemap_idx:
                    Tilemap = RawTilemap(Path(databin_dir, f'{int(tilemap_idx):04d}.tilemap'))

                linear_flag = (linear != '')
                if OAM_width: OAM_width = int(OAM_width)
                if OAM_height: OAM_height = int(OAM_height)

                canva = ImageCanva(Bitmap=Bitmap, Palette=Palette, Tilemap=Tilemap,
                               bit_depth=int(bpp), im_size=(int(im_width), int(im_height)),
                               OAM_size=(OAM_width, OAM_height), linear=linear_flag)
            
                canva.import_image(png_path)

                Bitmap.write(Path(new_databin_dir, f'{int(bitmap_idx):04d}.{bpp}bpp'))
                Palette.write(Path(new_databin_dir, f'{int(palette_idx):04d}.ndspal'))
                if Tilemap: Tilemap.write(Path(new_databin_dir, f'{int(tilemap_idx):04d}.tilemap'))