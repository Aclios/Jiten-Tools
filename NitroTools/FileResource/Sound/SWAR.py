from NitroTools.FileSystem import EndianBinaryReader, EndianBinaryFileWriter
from NitroTools.FileResource.File import File
from NitroTools.FileResource.Sound.ADPCM import decode_block

from pathlib import Path
import os

class SWAR(File):
    '''
    Load a SWAR file (Sound WAve Resource(?)), which contains one or several sound effects.
    They can be coded in three different codecs: 8PCM, 16PCM, or ADPCM.
    '''
    def read(self, f : EndianBinaryReader):
        self.magic = f.check_magic(b"SWAR")
        self.unk = f.read_UInt32()
        self.filesize = f.read_UInt32()
        self.header_size = f.read_UInt16()
        self.block = f.read_UInt16()
        self.data = SWARDATA(f)

    def extract(self, out_dir):
        for idx, entry in enumerate(self.data.entries):
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            entry.to_wav(Path(out_dir) / f"swav_{idx}.wav")

class SWARDATA:
    def __init__(self, f : EndianBinaryReader):
        f.check_magic(b"DATA")
        self.size = f.read_Int32()
        padding = f.read(0x20)
        self.entry_count = f.read_Int32()
        self.entry_offsets = [f.read_Int32() for _ in range(self.entry_count)]
        self.entry_size = []
        for i in range(self.entry_count - 1):
            self.entry_size.append(self.entry_offsets[i + 1] - self.entry_offsets[i])
        if self.entry_count > 0:
            self.entry_size.append(self.size - self.entry_offsets[-1])
        self.entries : list[SWAREntry] = []
        for i in range(self.entry_count):
            f.seek(self.entry_offsets[i])
            entry = SWAREntry(f)
            entry.data = f.read(self.entry_size[i])
            self.entries.append(entry)

class SWAREntry:
    data : bytes
    def __init__(self, f : EndianBinaryReader):
        self.type = f.read_UInt8()
        self.loop = f.read_UInt8()
        self.samplerate = f.read_UInt16()
        self.time = f.read_UInt16()
        self.loop_offset = f.read_UInt16()
        self.nonloop_size = f.read_UInt32()

    def to_wav(self, out_filepath):
        if self.type == 0: #PCM8
            write_pcm_wav(self.data, 8, self.samplerate, out_filepath)
        elif self.type == 1: #PCM16
            write_pcm_wav(self.data, 16, self.samplerate, out_filepath)
        else: #ADPCM
            decoded_data = decode_block(self.data)
            write_pcm_wav(decoded_data, 16, self.samplerate, out_filepath)

def write_pcm_wav(data : bytes, pcm : int, samplerate : int, filepath : str):
    with EndianBinaryFileWriter(filepath) as f:
        assert pcm in [8,16]
        f.write(b"RIFF")
        f.write_Int32(44 + len(data) - 8)
        f.write(b"WAVEfmt ")
        f.write_Int32(0x10)
        f.write_Int16(1)
        f.write_Int16(1)
        f.write_Int32(samplerate)
        f.write_Int32(samplerate * pcm // 8)
        f.write_Int16(pcm // 8)
        f.write_Int16(pcm)
        f.write(b"data")
        f.write_Int32(len(data))
        f.write(data)