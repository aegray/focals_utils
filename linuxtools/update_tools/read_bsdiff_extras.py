

import struct
import sys
import os
import glob


def getstuff(fname):
    fullsize = os.stat(fname).st_size
    with open(fname, 'rb') as fin:
        magic = fin.read(8)
        cmp_control_len = struct.unpack('<Q', fin.read(8))[0]
        cmp_diff_len = struct.unpack('<Q', fin.read(8))[0]
        tgt_len = struct.unpack('<Q', fin.read(8))[0]
        cmp_extra_len = fullsize - cmp_control_len - cmp_diff_len - 8 * 4

    return dict(file=fname, magic=magic, control_len=cmp_control_len, diff_len=cmp_diff_len, extra_len=cmp_extra_len, tgt_len=tgt_len)


parts = []

for file in sys.argv[1:]:
    parts.append(getstuff(file))


parts = sorted(parts, key=lambda x: x['extra_len'])

for x in parts:
    print(x)

#
#with open(sys.argv[1], 'rb') as fin:
#    magic = fin.read(8)
#    cmp_control_len = struct.unpack('<Q', fin.read(8))[0]
#    cmp_diff_len = struct.unpack('<Q', fin.read(8))[0]
#    tgt_len = struct.unpack('<Q', fin.read(8))[0]
#    cmp_extra_len = fullsize - cmp_control_len - cmp_diff_len - 8 * 4
#
#    print(f"file={sys.argv[1]} magic={magic} control_len={cmp_control_len} diff_len={cmp_diff_len} extra_len={cmp_extra_len} tgt_len={tgt_len}")
#    #print("Magic: ", magic)
#    #print("Control bz2 len: ", cmp_control_len)
#    #print("Diff bz2 len: ", cmp_diff_len)
#    #print("Extra len: ", cmp_extra_len)
#    #print("Tgt len: ", tgt_len)
#
#
#
#
#
#
