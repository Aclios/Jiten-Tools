from NitroTools.FileSystem import EndianBinaryStreamReader
from struct import pack

class DecompressionError(ValueError):
    pass

def decompress_raw_rle(in_data : bytes, decompressed_size : int) -> bytearray:
    out_data = bytearray()
    stream = EndianBinaryStreamReader(in_data)

    while len(out_data) < decompressed_size:

        decode_value = stream.read_UInt8()

        if decode_value <= 127:
            out_data += stream.read(decode_value + 1)

        else:
            out_data += stream.read(1) * (decode_value - 125)
    
    if len(out_data) != decompressed_size:
        raise DecompressionError("Decompressed size does not match the expected size")
    
    return out_data

def decompress_rle(in_data : bytes) -> bytearray:
    stream = EndianBinaryStreamReader(in_data)
    info = stream.read_UInt32()
    magic = info & 0xff
    decompressed_size = info >> 8
    if magic != 0x30:
        raise DecompressionError(f"Invalid magic, expected 0x30, got {hex(magic)}")
    return decompress_raw_rle(in_data[4:], decompressed_size)

def compress_raw_rle(in_data : bytes):
    out_data = bytearray()
    idx = 0
    while idx < len(in_data):
        stream = bytearray()
        first_byte = in_data[idx]
        stream.append(first_byte)
        idx += 1

        while idx < len(in_data) and in_data[idx] == first_byte and len(stream) < 130:
            stream.append(in_data[idx])
            idx += 1

        if len(stream) > 2: #encode consecutive identical bytes
            out_data.append(len(stream) + 125)
            out_data.append(first_byte)

        else: #encode consecutive different bytes
            reps = 1
            comp_byte = in_data[idx]
            stream.append(comp_byte)
            idx += 1
            while idx < len(in_data) and len(stream) < 128:
                stream.append(in_data[idx])
                if comp_byte == in_data[idx]:
                    reps += 1
                    if reps == 3: # if the last 3 bytes are identical, we remove them from the stream and go back
                        idx -= 2
                        stream = stream[:-3]
                        break
                else:
                    reps = 1
                    comp_byte = in_data[idx] 
                idx += 1
                
            out_data.append(len(stream) - 1)
            out_data += stream

    return out_data

def compress_rle(in_data : bytes):
    return bytearray(pack("<L", (len(in_data) << 8) + 0x30)) + compress_raw_rle(in_data)