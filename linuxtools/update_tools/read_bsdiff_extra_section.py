
import sys
import os
import struct
import bz2
import tempfile


def getstuff(fname):
    fullsize = os.stat(fname).st_size
    with open(fname, 'rb') as fin:
        magic = fin.read(8)
        cmp_control_len = struct.unpack('<Q', fin.read(8))[0]
        cmp_diff_len = struct.unpack('<Q', fin.read(8))[0]
        tgt_len = struct.unpack('<Q', fin.read(8))[0]
        cmp_extra_len = fullsize - cmp_control_len - cmp_diff_len - 8 * 4

    return dict(file=fname, magic=magic, control_len=cmp_control_len, diff_len=cmp_diff_len, extra_len=cmp_extra_len, tgt_len=tgt_len)


inf = sys.argv[1]
#outf = sys.argv[2]


data = getstuff(inf)

decomp = bz2.BZ2Decompressor()



with open(inf, 'rb') as fin:
    fin.seek(8*4 + data['control_len'] + data['diff_len'])

    data = fin.read()

    data = decomp.decompress(data)

    with tempfile.NamedTemporaryFile(mode='wb') as fout:
        fout.write(data)


        os.system("strings %s"%(fout.name))

    #with open('./tmpout.txt', 'wb') as fout:
    #    fout.write(data)
    #with open(outf, 'wb') as fout:
    #    fout.write(data)


