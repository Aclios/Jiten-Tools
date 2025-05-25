import csv
from NitroTools.FileSystem import EndianBinaryReader, EndianBinaryStreamWriter
from NitroTools.FileResource import File
from NitroTools.Compression import decompress_lz10, decompress_rle, compress_lz10, compress_rle
from pathlib import Path

class JitenDatabin(File):
    def read(self, f : EndianBinaryReader):
        self.file_count = f.read_Int32()
        self.files = [DatabinFile(f) for _ in range(self.file_count)]

    def unpack(self, extract_dir : str, fileinfo_path : str):
     #   if os.path.isdir(extract_dir):
      #      raise Exception('Extracted folder already exists, please delete it if you want to extract the files again (safety measure)')

        Path(extract_dir).mkdir(exist_ok=True)
        
        with open(fileinfo_path, mode='r', encoding = 'utf-8', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                idx, compression, extension = row
                assert extension != "", idx
                idx = int(idx)
                print(f"Unpack {idx}.{extension}...")
                data = self.files[idx].data
                if compression == "":
                    pass
                elif compression == "lz10":
                    data = decompress_lz10(data)
                elif compression == "rle":
                    data = decompress_rle(data)
                else:
                    raise Exception(f'Unknown compression: {compression}')
                open(Path(extract_dir) / ("{:04d}".format(idx) + f".{extension}"), 'wb').write(data)

    def import_files(self, import_dir : str, fileinfo_path : str):
        with open(fileinfo_path, mode='r', encoding = 'utf-8', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                idx, compression, extension = row
                assert extension != "", idx
                idx = int(idx)
                lookup_path = Path(import_dir) / ("{:04d}".format(idx) + f".{extension}")
                if lookup_path.exists():
                    data = open(lookup_path, 'rb').read()
                    if compression == "":
                        pass
                    elif compression == "lz10":
                        data = compress_lz10(data)
                    elif compression == "rle":
                        data = compress_rle(data)
                    else:
                        raise Exception(f'Unknown compression: {compression}')
                    self.files[idx].data = data
                    self.files[idx].size = len(data)

    def to_bytes(self):
        f = EndianBinaryStreamWriter()
        f.write_Int32(self.file_count)
        offset = self.file_count * 8 + 4
        for file in self.files:
            f.write_Int32(offset)
            f.write_Int32(file.size)
            offset += file.size
            offset = align(offset, 4)
        for file in self.files:
            f.write(file.data)
            f.pad(4)
        return f.getvalue()

class DatabinFile:
    def __init__(self, f : EndianBinaryReader):
        self.offset = f.read_Int32()
        self.size = f.read_Int32()
        pos = f.tell()
        f.seek(self.offset)
        self.data = f.read(self.size)
        f.seek(pos)

def align(value : int, alignment : int):
    mod = value % alignment
    if mod != 0:
        value += (alignment - mod)
    return value