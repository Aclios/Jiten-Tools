from NitroTools.FileSystem import EndianBinaryReader
from NitroTools.FileResource.File import File
import os
from pathlib import Path
from NitroTools.FileResource.Sound.SWAR import SWAR

class SDAT(File):
    '''
    Load an SDAT (Sound DATa) file, which is an archive containing BGMs and sound effects.
    '''
    def read(self, f : EndianBinaryReader):
        self.magic = f.check_magic(b"SDAT")
        self.unk = f.read_UInt32()
        self.filesize = f.read_UInt32()
        self.header_size = f.read_UInt16()
        self.section_count = f.read_UInt16()
        assert self.section_count == 4, f"Unsupported SDAT format with {self.section_count} sections"

        self.symb_offset = f.read_UInt32()
        self.symb_size = f.read_UInt32()
        self.info_offset = f.read_UInt32()
        self.info_size = f.read_UInt32()
        self.fat_offset = f.read_UInt32()
        self.fat_size = f.read_UInt32()
        self.data_offset = f.read_UInt32()
        self.data_size = f.read_UInt32()

        f.seek(self.symb_offset)
        self.symb = SDAT_SYMB(f)

        f.seek(self.info_offset)
        self.info = SDAT_INFO(f)

        f.seek(self.fat_offset)
        self.fat = SDAT_FAT(f)

    def unpack(self, out_dir : str):
        if not (Path(out_dir) / "SSEQ").exists():
            os.makedirs(Path(out_dir) / "SSEQ")

        if not (Path(out_dir) / "SSAR").exists():
            os.makedirs(Path(out_dir) / "SSAR")

        if not (Path(out_dir) / "SBNK").exists():
            os.makedirs(Path(out_dir) / "SBNK")

        if not (Path(out_dir) / "SWAR").exists():
            os.makedirs(Path(out_dir) / "SWAR")

        if not (Path(out_dir) / "STRM").exists():
            os.makedirs(Path(out_dir) / "STRM")

        for idx, sseq_info in enumerate(self.info.sseq_info):
            name = self.symb.sseq_names[idx]
            data = self.fat.entries[sseq_info.id].data
            open(Path(out_dir) / "SSEQ" / (name + ".sseq"),'wb').write(data)

        for idx, ssar_info in enumerate(self.info.ssar_info):
            name = self.symb.ssar_names[idx]
            data = self.fat.entries[ssar_info.id].data
            open(Path(out_dir) / "SSAR" / (name + ".ssar"),'wb').write(data)

        for idx, sbnk_info in enumerate(self.info.sbnk_info):
            name = self.symb.sbnk_names[idx]
            data = self.fat.entries[sbnk_info.id].data
            open(Path(out_dir) / "SBNK" / (name + ".sbnk"),'wb').write(data)

        for idx, swar_info in enumerate(self.info.swar_info):
            name = self.symb.swar_names[idx]
            data = self.fat.entries[swar_info.id].data
            swar = SWAR(data)
            swar.extract(Path(out_dir) / "SWAR" / name)

        for idx, strm_info in enumerate(self.info.strm_info):
            name = self.symb.strm_names[idx]
            data = self.fat.entries[strm_info.id].data
            open(Path(out_dir) / "STRM" / (name + ".strm"),'wb').write(data)

class SDAT_SYMB:
    '''
    SDAT mandatory section. Contains file names.
    '''
    def __init__(self, f : EndianBinaryReader):
        self.start_offset = f.tell()
        self.magic = f.check_magic(b"SYMB")
        self.section_size = f.read_UInt32()
        entries = [self.read_entry(f) for _ in range(8)]
        self.sseq_names, self.ssar_names, self.sbnk_names, self.swar_names, self.player_names, self.group_names, self.player2_names, self.strm_names = entries

    def read_entry(self, f : EndianBinaryReader):
        names_table_offset = f.read_UInt32()
        pos = f.tell()
        f.seek(names_table_offset + self.start_offset)
        entry_count = f.read_UInt32()
        name_offsets = [f.read_UInt32() for _ in range(entry_count)]
        names = []
        for offset in name_offsets:
            if offset != 0:
                f.seek(offset + self.start_offset)
                names.append(f.read_string_until_null().decode("shift-jis-2004"))
        f.seek(pos)
        return names

class SYMB_Entry:
    def __init__(self, f : EndianBinaryReader, start_offset : int):
        self.names_table_offset = f.read_UInt32()
        pos = f.tell()
        f.seek(self.names_table_offset + start_offset)
        self.entry_count = f.read_UInt32()
        self.name_offsets = [f.read_UInt32() for _ in range(self.entry_count)]
        self.names = []
        for offset in self.name_offsets:
            f.seek(offset + start_offset)
            self.names.append(f.read_string_until_null().decode("shift-jis-2004"))
        f.seek(pos)
        
class SDAT_INFO:
    '''
    SDAT mandatory section. Contains parameters for each file: for example ids, volume, associated files, etc.
    '''
    def __init__(self, f : EndianBinaryReader):
        self.start_offset = f.tell()
        self.magic = f.check_magic(b"INFO")
        self.section_size = f.read_UInt32()
        self.sseq_info : list[SSEQ_INFO] = self.read_entry(f, SSEQ_INFO)
        self.ssar_info : list[SSAR_INFO]= self.read_entry(f, SSAR_INFO)
        self.sbnk_info : list[SBNK_INFO]= self.read_entry(f, SBNK_INFO)
        self.swar_info : list[SWAR_INFO]= self.read_entry(f, SWAR_INFO)
        self.player_info : list[PLAYER_INFO]= self.read_entry(f, PLAYER_INFO)
        self.group_info : list[GROUP_INFO]= self.read_entry(f, GROUP_INFO)
        self.player2_info : list[PLAYER2_INFO]= self.read_entry(f, PLAYER2_INFO)
        self.strm_info : list[STRM_INFO]= self.read_entry(f, STRM_INFO)

    def read_entry(self, f : EndianBinaryReader, TypeINFO):
        offset = f.read_UInt32() + self.start_offset
        pos = f.tell()
        f.seek(offset)
        entry_count = f.read_UInt32()
        entry_offsets = [f.read_UInt32() for _ in range(entry_count)]
        entries = []
        for offset in entry_offsets:
            if offset != 0:
                f.seek(offset + self.start_offset)
                entries.append(TypeINFO(f))
        f.seek(pos)
        return entries

class SSEQ_INFO:
    def __init__(self, f : EndianBinaryReader):
        self.id = f.read_UInt16()
        self.unk = f.read_UInt16()
        self.bank = f.read_UInt16()
        self.volume = f.read_UInt8()
        self.channel_pressure = f.read_UInt8()
        self.polyphonic_pressure = f.read_UInt8()
        self.play = f.read_UInt16()
        padding = f.read(1)

class SSAR_INFO:
    def __init__(self, f : EndianBinaryReader):
        self.id = f.read_UInt16()
        self.unk = f.read_UInt16()

class SBNK_INFO:
    def __init__(self, f : EndianBinaryReader):
        self.id = f.read_UInt16()
        self.unk = f.read_UInt16()
        self.associated_swar1 = f.read_UInt16()
        self.associated_swar2 = f.read_UInt16()
        self.associated_swar3 = f.read_UInt16()
        self.associated_swar4 = f.read_UInt16()

class SWAR_INFO:
    def __init__(self, f : EndianBinaryReader):
        self.id = f.read_UInt16()
        self.unk = f.read_UInt16()

class PLAYER_INFO:
    def __init__(self, f : EndianBinaryReader):
        self.unk1 = f.read_UInt32()
        self.unk2 = f.read_UInt32()

class STRM_INFO:
    def __init__(self, f : EndianBinaryReader):
        self.id = f.read_UInt16()
        pass

class PLAYER2_INFO:
    def __init__(self, f : EndianBinaryReader):
        pass

class GROUP_INFO:
    def __init__(self, f : EndianBinaryReader):
        pass

class SDAT_FAT:
    '''
    SDAT mandatory section. File Access Table, containing offsets and sizes of the actual files.
    '''
    def __init__(self, f : EndianBinaryReader):
        self.start_offset = f.tell()
        self.magic = f.check_magic(b"FAT ")
        self.section_size = f.read_UInt32()
        self.entry_count = f.read_UInt32()
        self.entries = [FAT_Entry(f) for _ in range(self.entry_count)]
        for entry in self.entries:
            entry.read_data(f)

class FAT_Entry:
    def __init__(self, f : EndianBinaryReader):
        self.data_offset = f.read_UInt32()
        self.data_size = f.read_UInt32()
        self.unk1 = f.read_UInt32()
        self.unk2 = f.read_UInt32()

    def read_data(self, f : EndianBinaryReader):
        f.seek(self.data_offset)
        self.data = f.read(self.data_size)