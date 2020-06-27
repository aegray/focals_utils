
# https://android.googlesource.com/platform/bootable/recovery/+/9885851f626081c27131d482115c9b656688beaa/applypatch/imgdiff.c
import sys
import os
import struct
import bz2
import tempfile

#
#def getstuff(fname):
#    fullsize = os.stat(fname).st_size
#    with open(fname, 'rb') as fin:
#        magic = fin.read(8)
#        cmp_control_len = struct.unpack('<Q', fin.read(8))[0]
#        cmp_diff_len = struct.unpack('<Q', fin.read(8))[0]
#        tgt_len = struct.unpack('<Q', fin.read(8))[0]
#        cmp_extra_len = fullsize - cmp_control_len - cmp_diff_len - 8 * 4
#
#    return dict(file=fname, magic=magic, control_len=cmp_control_len, diff_len=cmp_diff_len, extra_len=cmp_extra_len, tgt_len=tgt_len)
#


CHUNK_NORMAL = 0
CHUNK_GZIP = 1
CHUNK_DEFLATE = 2
CHUNK_RAW = 3

GZIP_HEADER_LEN=10
GZIP_FOOTER_LEN=8

inf = sys.argv[1]

with open(inf, 'rb') as f:
    magic = f.read(8)
    chunk_count = struct.unpack('<I', f.read(4))[0]

    print("Nchunk", chunk_count)
    for i in range(chunk_count):
        chunk_type = struct.unpack('<I', f.read(4))[0]
        print("Chunk type", chunk_type)

        if chunk_type == CHUNK_NORMAL:
            src_start, src_len, bsdiff_patchoff = struct.unpack('<QQQ', f.read(8*3))
        elif chunk_type == CHUNK_GZIP:
            parts = struct.unpack('<QQQQQIIIIII', f.read(8*5+4*6))
            hdr_len = parts[-1]
            gzip_header = f.read(hdr_len)
            gzip_footer = f.read(8)
        elif chunk_type == CHUNK_DEFLATE:
            parts = struct.unpack('<QQQQQIIIII', f.read(8*5+4*5))
        elif chunk_type == CHUNK_RAW:
            tgt_len = struct.unpack('<I', f.read(4))
            data = f.read(tgt_len)
        else:
            raise ValueError("Unexpected chunk_type: ", chunk_type)

#
#
##outf = sys.argv[2]
#
#
#data = getstuff(inf)
#
#decomp = bz2.BZ2Decompressor()
#
#
#
#
#
#
#with open(inf, 'rb') as fin:
#    fin.seek(8*4 + data['control_len'] + data['diff_len'])
#
#    data = fin.read()
#
#    data = decomp.decompress(data)
#
#    with tempfile.NamedTemporaryFile(mode='wb') as fout:
#        fout.write(data)
#
#        os.system("strings %s"%(fout.name))
#
#    #with open('./tmpout.txt', 'wb') as fout:
#    #    fout.write(data)
#    #with open(outf, 'wb') as fout:
#    #    fout.write(data)
#

