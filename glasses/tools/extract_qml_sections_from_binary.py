

import sys
import struct


def process_section(data, start, end):
    onind = start

    entries = []

    #return ((start, end, data[start:end]))

    while onind < end:
        ilen, = struct.unpack("I", data[onind:(onind+4)])
        if ilen == 0:
            # ignore empty bytes
            onind += 4
        else:

            vlen = ilen + (ilen%2)
            #print(ilen, ilen%2, vlen)

            new_onind = onind + 4 + vlen*2
            #print("ilen=", ilen, "onind=", hex(onind), " new_onind=", hex(new_onind)) #, " adjmod=", adj % 4)

            sent = data[(onind+4):(onind+4+vlen*2):2]

            entries.append(sent)

            onind = new_onind

    return entries


def process_file(fname):

    data = open(fname, 'rb').read()

    # Find QtQuick header (each byte separated by null bytes), go back 4 bytes
    # Find footer (qv4cdata - no separation)
    #   1) Q.t.Q.u.i.c.k as a start -> 07 00 00 00 51 00 74 00 51 00 75 00 69 00 63 00 6B

    def find_all(a_str, sub):
        start = 0
        while True:
            start = a_str.find(sub, start)
            if start == -1: return
            yield start
            start += len(sub)


    header = (b'\x51\x00\x74\x00\x51\x00\x75\x00\x69\x00\x63\x00\x6B')

    footer = b'\x71\x76\x34\x63\x64\x61\x74\x61\x13'


    start_offsets = list(find_all(data, header))
    footers = list(find_all(data, footer))


    onind_start = 0
    onind_end = 0


    real_start = start_offsets[onind_start] - 4

    section_index = 0


    while (onind_end < len(footers)):
        cur_end = footers[onind_end]
        if onind_start < len(start_offsets) and start_offsets[onind_start] < cur_end:
            # move start ptr forward to find next section
            onind_start += 1
        else:
            # process section
            onind_end += 1


            res = process_section(data, real_start, cur_end)

            print("==========================================")
            print(f"Section {section_index}:")
            print("==========================================")
            print(res)

            section_index += 1


            if onind_start > len(start_offsets):
                break

            real_start = start_offsets[onind_start] - 4

            onind_start += 1




if __name__ == '__main__':
    process_file(sys.argv[1])





