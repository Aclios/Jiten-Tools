from subprocess import check_call
from pathlib import Path
from JitenTools import (
    JitenDatabin, 
    export_images, 
    import_images,
    export_encyclopedia,
    import_encyclopedia, 
    export_openings,
    import_openings,
    import_fonts
)
from shutil import copy2, copytree
from sys import argv

def extract_data(rom_path : str):
    check_call([Path('cltools', 'dsrom'), 'extract', '--rom', rom_path, '--path', Path('_project', 'original', 'rom')])
    copytree(Path('_project', 'original', 'rom'), Path('_project', 'new', 'rom'))

    databin = JitenDatabin(Path('_project', 'original', 'rom', 'files', 'data.bin'))
    databin.unpack(Path('_project', 'original', 'databin'), Path('mapping', 'fileinfo.csv'))

    export_images(Path('_project', 'original', 'databin'), Path('_project', 'original', 'images'), Path('mapping', 'filemap.csv'))

    export_encyclopedia(Path('_project', 'original', 'rom', 'arm9', 'arm9.bin'), Path('_project', 'new', 'text', 'encyclopedia'))

    export_openings(Path('_project', 'original', 'rom', 'arm9', 'arm9.bin'), Path('_project', 'new', 'text', 'script'))

def import_data(rom_path : str):
    print('Copying old arm9.bin...\n')
    copy2(Path('_project', 'original', 'rom', 'arm9', 'arm9.bin'), Path('_project', 'new', 'rom', 'arm9', 'arm9.bin'))

    print('Importing openings and credits...\n')
    import_openings(
        Path('_project', 'new', 'rom', 'arm9', 'arm9.bin'),
        Path('_project', 'new', 'text', 'script'),
        Path('_project', 'new', 'font', 'fontmap.csv')
        )

    print('\nImporting encyclopedia...\n') 
    import_encyclopedia(
        Path('_project', 'new', 'rom', 'arm9', 'arm9.bin'),
        Path('_project', 'new', 'text', 'encyclopedia', 'encyclopedia.xlsx'),
        Path('_project', 'new', 'font', 'fontmap.csv')
        )
    
    print('Importing font...\n')
    import_fonts(Path('_project', 'new', 'rom', 'arm9', 'arm9.bin'), Path('_project', 'new', 'font'))

    print('Importing images...\n')
    import_images(
        Path('_project', 'original', 'databin'),
        Path('_project', 'new', 'images'),
        Path('mapping', 'filemap.csv'),
        Path('_project', 'new', 'databin')
    )

    print('\nWriting assembly hacks...\n')
    check_call([Path('cltools', 'armips'), '-erroronwarning', Path('asm' ,'hacks.S')])
    check_call([Path('cltools', 'armips'), '-erroronwarning', Path('asm' ,'memory.S')])
    check_call([Path('cltools', 'armips'), '-erroronwarning', Path('asm' ,'oam.S')])

    print('Importing new files to data.bin...\n')
    databin = JitenDatabin(Path('_project', 'original', 'rom', 'files', 'data.bin'))
    databin.import_files(Path('_project', 'new', 'databin'), Path('mapping', 'fileinfo.csv'))
    databin.write(Path('_project', 'new', 'rom', 'files', 'data.bin'))

    print('Building rom...\n')
    check_call([Path('cltools', 'dsrom'), 'build', '--rom', rom_path, '--config', Path('_project', 'new', 'rom', 'config.yaml')])

def main():
    if len(argv) == 3 and argv[1] == '-e':
        extract_data(argv[2])
    elif len(argv) == 3 and argv[1] == '-i':
        import_data(argv[2])
    else:
        print(
'''
Usage: 
Extract files from the original rom: py main.py -e [path_of_the_rom]
Build new rom: py main.py -i [path_of_the_new_rom]''')

if __name__ == '__main__':
    main()