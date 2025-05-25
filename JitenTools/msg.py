from NitroTools.FileSystem import EndianBinaryFileReader, EndianBinaryFileUpdater
from .enums import description_offset_pos
from .font import parse_fontmap
from io import StringIO
import pandas as pd
from pathlib import Path
from typing import List

WRITE_TEXT_START = 0x6AEF0
WRITE_TEXT_END = 0x92100

def extract_jp_descriptions(arm9_path: str):
    message_data = []
    with EndianBinaryFileReader(arm9_path) as f:
        for msg_offset_pos in description_offset_pos:
            f.seek(int(msg_offset_pos, 16))
            msg_offset = f.read_UInt32() % 0x2000000
            f.seek(msg_offset)
            message_data.append([read_description_string(f), int(msg_offset_pos, 16)])
    return message_data

def read_description_string(f : EndianBinaryFileReader) -> str:
        output = ""
        jump_flag = False
        while True:
            data = f.read(2).decode('shift-jis-2004')
            if len(data) == 0:
                raise Exception("EOF reached")
            elif data == "#a":
                if jump_flag:
                    output += "</JUMP>"
                    jump_flag = False
                else:
                    numbers = f.read(4).decode('shift-jis-2004')
                    output += f"<JUMP:{numbers}>"
                    jump_flag = True
            elif data == "#n":
                output += "\n"
            elif data in ["#e", "#p", "\x00\x00"]:
                return output
            else:
                output += data

def export_encyclopedia(arm9_path : str, out_dir : str):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    excel_path = Path(out_dir, "encyclopedia.xlsx")
    if excel_path.exists():
        raise Exception("encyclopedia.xlsx already exists.")
    message_data = extract_jp_descriptions(arm9_path)
    data = [[hex(offset), string, string] for string, offset in message_data]
    df = pd.DataFrame(data=data, columns=["Pointer offset", "Original", "Translation"])
    df.to_excel(excel_path)

def import_encyclopedia(arm9_path : str, encyclopedia_path : str, fontmap_path : str):
    df = pd.read_excel(encyclopedia_path)
    _ , characters = parse_fontmap(fontmap_path)
    data : List[tuple[int, bytes]] = []
    for idx, string in enumerate(df["Translation"]):
        pointer_offset = int(df["Pointer offset"][idx], 16)
        databyte = encyclopedia_string_to_bytes(string, characters)
        data.append([pointer_offset, databyte])
    with EndianBinaryFileUpdater(arm9_path) as f:
        offset = WRITE_TEXT_START
        for pointer_offset, databyte in data:
            f.seek(offset)
            f.write(databyte)
            pos = f.tell()
            f.seek(pointer_offset)
            f.write_UInt32(offset + 0x2_00_00_00)
            offset = pos
            if offset > WRITE_TEXT_END:
                raise Exception("Text data is overflowing the available space, another area must be found. Aborting.")


def encyclopedia_string_to_bytes(string : str, chars : list[str]):
    output = bytes()
    f = StringIO(string)
    char = f.read(1)
    while char != "":
        if char == '\n':
            output += b"#n"

        elif char == '<':
            jump_code = ""
            while char != '>':
                jump_code += char
                char = f.read(1)
            output += b"#a"
            if jump_code != "</JUMP":
                output += jump_code.split(":")[1].encode()     

        else:
            if char in chars:
                output += chars.index(char).to_bytes(1, 'little')

        char = f.read(1)

    output += b"#e"
    return output