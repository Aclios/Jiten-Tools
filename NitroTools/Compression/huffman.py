from NitroTools.FileSystem import EndianBinaryStreamReader, EndianBinaryStreamWriter
from struct import pack

class DecompressionError(ValueError):
    pass

def decompress_huffman4bits(in_data : bytes) -> bytearray:
    stream = EndianBinaryStreamReader(in_data)
    info = stream.read_UInt32()
    magic = info & 0xff
    decompressed_size = info >> 8
    if magic != 0x24:
        raise DecompressionError(f"Invalid magic, expected 0x24, got {hex(magic)}")
    return decompress_raw_huffman4bits(in_data[4:], decompressed_size)

def decompress_huffman8bits(in_data : bytes) -> bytearray:
    stream = EndianBinaryStreamReader(in_data)
    info = stream.read_UInt32()
    magic = info & 0xff
    decompressed_size = info >> 8
    if magic != 0x28:
        raise DecompressionError(f"Invalid magic, expected 0x28, got {hex(magic)}")
    return decompress_raw_huffman8bits(in_data[4:], decompressed_size)

def decompress_raw_huffman4bits(in_data : bytes, decompressed_size : int):
    return decompress_raw_huffman(in_data, decompressed_size, 4)

def decompress_raw_huffman8bits(in_data : bytes, decompressed_size : int):
    return decompress_raw_huffman(in_data, decompressed_size, 8)

def decompress_raw_huffman(in_data : bytes, decompressed_size : int, num_bits : int):
    out_data = bytearray(decompressed_size)
    stream = EndianBinaryStreamReader(in_data)
    mask = 0
    nbits = 0
    out_pos = 0
    stream.seek((in_data[0] + 1) << 1)
    pos = in_data[1]
    N = len(in_data)

    while out_pos < decompressed_size:
        mask >>= 1
        if mask == 0:
            if stream.tell() + 3 > N:
                break
            code = stream.read_UInt32()
            mask = 0x80_00_00_00

        next = ((pos & 0x3F) + 1) << 1
        next &= 0xFF_FF_FF_FF

        if code & mask == 0:
            ch = pos & 0x80
            pos = in_data[next]
        else:
            ch = pos & 0x40
            pos = in_data[next + 1]

        if ch:
            out_data[out_pos] |= (pos << nbits)
            nbits = (nbits + num_bits) & 7
            if nbits == 0:
                out_pos += 1
            pos = in_data[1]
            next = 0

    return out_data

class HuffmanNode:
    symbol : int
    weight : int
    leafs = 1
    parent = None
    left = None
    right = None

class HuffmanCode:
    nbits : int
    codework : int

HUF_NEXT = 0x3F
HUF_LCHAR = 0x80
HUF_RCHAR = 0x40

def compress_raw_huffman(in_data : bytes, num_bits : int):

    def CreateCodeBranch(root : HuffmanNode, p : int, q : int):
        if root.leafs <= HUF_NEXT + 1:
            stack : list[HuffmanNode] = [None] * (2 * root.leafs)
            s = r = 0
            stack[r] = root
            r += 1

            while (s < r):
                node = stack[s]
                s += 1
                if node.leafs == 1:
                    if s == 1:
                        code_tree[p] = node.symbol
                        code_mask[p] = 0xFF
                    else:
                        code_tree[q] = node.symbol
                        code_mask[q] = 0xFF
                        q += 1

                else:
                    mask = 0
                    if node.left.leafs == 1: mask |= HUF_LCHAR
                    if node.right.leafs == 1: mask |= HUF_RCHAR
                    if s == 1:
                        code_tree[p] = (r - s) >> 1
                        code_mask[p] = mask
                    else:
                        code_tree[q] = (r - s) >> 1
                        code_mask[q] = mask
                        q += 1
                    stack[r] = node.left
                    stack[r+1] = node.right
                    r += 2
        else:
            mask = 0
            if root.left.leafs == 1: mask |= HUF_LCHAR
            if root.right.leafs == 1: mask |= HUF_RCHAR
            code_tree[p] = 0
            code_mask[p] = mask
            if root.left.leafs <= root.right.leafs:
                l_leafs = CreateCodeBranch(root.left, q, q + 2)
                r_leafs = CreateCodeBranch(root.right, q + 1, q + (l_leafs << 1))
                code_tree[q + 1] = l_leafs - 1
            else:
                r_leafs = CreateCodeBranch(root.right, q + 1, q + 2)
                l_leafs = CreateCodeBranch(root.left, q, q + (r_leafs << 1))
                code_tree[q] = r_leafs - 1
        return root.leafs

    max_symbols = 1 << num_bits
    freqs = [0] * max_symbols

    for byte in in_data:
        for nbits in range(8, 0, -num_bits):
            freqs[byte >> (8 - nbits)] += 1
            byte = (byte << nbits) & 0xFF

    num_leafs = 0
    for elem in freqs:
        if elem:
            num_leafs += 1
    
    if num_leafs < 2:
        if num_leafs == 1:
            pass
        
        num_leafs += 1
        while num_leafs < 2:
            for i in range(max_symbols):
                if not freqs[i]:
                    freqs[i] = 2
                    break
            num_leafs += 1
    
    num_nodes = (num_leafs << 1) - 1
    tree = [HuffmanNode()] * num_nodes
    num_node = 0
    for i in range(max_symbols):
        if freqs[i]:
            node = HuffmanNode()
            node.symbol = i
            node.weight = freqs[i]
            node.leafs = 1
            tree[num_node] = node
            num_node += 1

    while num_node < num_nodes:
        left = None
        right = None
        lweight = rweight = 0
        for i in range(num_node):
            if tree[i].parent is None:
                if not lweight or tree[i].weight < lweight:
                    rweight = lweight
                    right = left
                    lweight = tree[i].weight
                    left = tree[i]
                
                elif not rweight or tree[i].weight < rweight:
                    rweight = tree[i].weight
                    right = tree[i]

        node = HuffmanNode()
        node.symbol = num_node - num_leafs + max_symbols
        node.weight = left.weight + right.weight
        node.leafs = left.leafs + right.leafs
        node.parent = None
        node.left = left
        node.right = right
        node.left.parent = node
        node.right.parent = node
        tree[num_node] = node
        num_node += 1

    max_nodes = (((num_leafs - 1) | 1) + 1) << 1
    code_tree = [0] * max_nodes
    code_mask = [0] * max_nodes

    code_tree[0] = (num_leafs - 1) | 1
    i = 0

    CreateCodeBranch(tree[num_nodes - 1], i + 1, i + 2)

    max = (code_tree[0] + 1) << 1

    i = 1
    while (i < max):
        if (code_mask[i] != 0xFF) and (code_tree[i] > HUF_NEXT):
            if (i & 1) and (code_tree[i - 1] == HUF_NEXT):
                i -= 1
                inc = 1
            elif (not (i & 1)) and (code_tree[i+1] == HUF_NEXT):
                i += 1
                inc = 1
            else:
                inc = code_tree[i] - HUF_NEXT

            n1 = (i >> 1) + 1 + code_tree[i]
            n0 = n1 - inc

            l1 = n1 << 1
            l0 = n0 << 1

            tmp0 = code_tree[l1 : l1 + 2]
            tmp1 = code_mask[l1 : l1 + 2]

            for j in range(l1, l0, -2):
                code_tree[j : j + 2] = code_tree[j - 2 : j]
                code_mask[j : j + 2] = code_mask[j - 2 : j]

            code_tree[l0 : l0 + 2] = tmp0
            code_mask[l0 : l0 + 2] = tmp1

            code_tree[i] -= inc

            for j in range(i + 1, l0):
                if code_mask[j] != 0xFF:
                    k = (j >> 1) + 1 + code_tree[j]
                    if k >= n0 and k < n1: code_tree[j] += 1

            if code_mask[l0    ] != 0xFF: code_tree[l0    ] += inc
            if code_mask[l0 + 1] != 0xFF: code_tree[l0 + 1] += inc

            for j in range(l0 + 2, l1 + 2):
                if code_mask[j] != 0xFF:
                    k = (j >> 1) + 1 + code_tree[j]
                    if (k > n1): code_tree[j] -= 1
            
            i = (i | 1) - 2
        i += 1

    i = (code_tree[0] + 1) << 1
    i -= 1
    while i:
        if (code_mask[i] != 0xFF): code_tree[i] |= code_mask[i]
        i -= 1

    codes : list[HuffmanCode] = [None] * max_symbols
    scode = [0] * 100

    for i in range(num_leafs):
        node = tree[i]
        symbol = node.symbol
        nbits = 0
        while node.parent is not None:
            if node.parent.left == node: scode[nbits] = 0
            else: scode[nbits] = 1
            nbits += 1
            node = node.parent
                
        maxbytes = (nbits + 7) >> 3
        code = HuffmanCode()
        codes[symbol] = code
        code.nbits = nbits
        code.codework = [None] * maxbytes
        for j in range(maxbytes): code.codework[j] = 0
        mask = 0x80
        j = 0
        for nbit in range(nbits, 0, -1):
            if scode[nbit - 1]: code.codework[j] |= mask
            mask >>= 1
            if not mask:
                mask = 0x80
                j += 1

    length = (code_tree[0] + 1) << 1
    out = EndianBinaryStreamWriter()
    for i in range(length):
        out.write_UInt8(code_tree[i] % 256)
    mask4 = 0
    pk4 = None
    for byte in in_data:
        for nbits in range(8, 0, -num_bits):
            code = codes[byte & ((1 << num_bits) - 1)]
            length = code.nbits
            cwork = code.codework
            cwork_idx = 0
            mask = 0x80
            for _ in range(length, 0, -1):
                mask4 >>= 1
                if not mask4:
                    if pk4 is not None: out.write_UInt32(pk4)
                    mask4 = 0x80_00_00_00
                    pk4 = 0
                if cwork[cwork_idx] & mask: pk4 |= mask4
                mask >>= 1
                if not mask:
                    mask = 0x80
                    cwork_idx += 1
            byte >>= num_bits

    out.write_UInt32(pk4)
    return out.getvalue()

def compress_raw_huffman4bits(in_data : bytes):
    return compress_raw_huffman(in_data, 4)

def compress_raw_huffman8bits(in_data : bytes):
    return compress_raw_huffman(in_data, 8)

def compress_huffman4bits(in_data : bytes):
    return bytearray(pack("<L", (len(in_data) << 8) + 0x24)) + compress_raw_huffman4bits(in_data)

def compress_huffman8bits(in_data : bytes):
    return bytearray(pack("<L", (len(in_data) << 8) + 0x28)) + compress_raw_huffman8bits(in_data)