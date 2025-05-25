from NitroTools.FileSystem import EndianBinaryFileReader, EndianBinaryFileUpdater, EndianBinaryStreamWriter
from .enums import opening_pointers, code_info
from .font import parse_fontmap
from pathlib import Path

WRITE_TEXT_START = 0xA3630
WRITE_TEXT_END = 0xBD33C

def export_openings(arm9_path : str, out_dir : str):
    Path(out_dir).mkdir(parents = True, exist_ok = True)
    with EndianBinaryFileReader(arm9_path) as f:
        for filename, opening_pointer_offset in opening_pointers.items():
            f.seek(int(opening_pointer_offset, 16))
            script_offset = f.read_UInt32() % 0x2000000
            f.seek(script_offset)
            script_data = read_opening(f)
            filepath = Path(out_dir, filename)
            print(f'Writing {filepath}...')
            open(filepath, 'w', encoding='utf-8').write(script_data)

def read_opening(f : EndianBinaryFileReader) -> str:
    string = ""
    value = f.read_UInt16()
    while True:
        if value < 0x8000:
            name, arg_count = code_info[hex(value)]
            if arg_count == 0:
                string += f"<{name}>"
                if value == 8:
                    string += '<NewLine>\n'
            else:
                args = [str(f.read_Int16()) for _ in range(arg_count)]
                string += f"<{name}:{','.join(args)}>"
                if value in [0x12,6,0x15]:
                    string += '\n'
            if value == 0x36:
                return string
        else:
            if value == 0x81a0:
                string += " "
            else:
                string += value.to_bytes(2,'big').decode('shift-jis-2004')
        value = f.read_UInt16()

def import_openings(arm9_path : str, openings_dir : str, fontmap_path : str):
    _ , characters = parse_fontmap(fontmap_path)
    data = []
    for filename, pointer_offset in opening_pointers.items():
        databyte = opening_string_to_bytes(Path(openings_dir, filename), characters)
        data.append([int(pointer_offset, 16), databyte, filename])
    with EndianBinaryFileUpdater(arm9_path) as f:
        offset = WRITE_TEXT_START
        for pointer_offset, databyte, filename in data:
            print(f'Importing {filename}...')
            f.seek(offset)
            f.write(databyte)
            pos = f.tell()
            f.seek(pointer_offset)
            f.write_UInt32(offset + 0x2_00_00_00)
            offset = pos
            if offset > WRITE_TEXT_END:
                raise Exception("Text data is overflowing the available space, another area must be found. Aborting.")

def opening_string_to_bytes(opening_path : str, chars : list[str]):
    reversed_codes = {v[0]:k[2:] for k,v in code_info.items()}
    stream = EndianBinaryStreamWriter()
    with open(opening_path, encoding='utf-8') as f: 
        char = f.read(1)
        while char != "":
            if char == "<":
                stream.write(parse_code(f, reversed_codes))
            elif char in ['\n','\r']:
                pass
            else:
                if char in chars:
                    value = chars.index(char) + 0x8000
                    stream.write_UInt16(value)
            char = f.read(1)
        return stream.getvalue()

def parse_code(f : EndianBinaryFileReader, code_dict : dict):
    char = f.read(1)
    data = ""
    while char != ">" and char != "":
        data += char
        char = f.read(1)
    if not ":" in data:
        return int(code_dict[data],16).to_bytes(2,'little')
    name, args = data.split(":")
    args = args.split(',')
    stream = EndianBinaryStreamWriter()
    stream.write_UInt16(int(code_dict[name],16))
    for arg in args:
        stream.write_Int16(int(arg))
    return stream.getvalue()