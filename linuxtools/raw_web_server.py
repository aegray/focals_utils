
import sys
import json
import socket
import hashlib
import base64
import struct
import itertools

TCP_PORT = int(sys.argv[1])
#8001


BUFFER_SIZE = 1024*20

GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

    #raw_key = bytes(random.getrandbits(8) for _ in range(16))
    #key = base64.b64encode(raw_key).decode()

def accept(key: str) -> str:
    sha1 = hashlib.sha1((key + GUID).encode()).digest()
    return base64.b64encode(sha1).decode()

        #s_w_key = headers["Sec-WebSocket-Key"]
        #raw_key = base64.b64decode(s_w_key.encode(), validate=True)

DATA_OPCODES = OP_CONT, OP_TEXT, OP_BINARY = 0x00, 0x01, 0x02
CTRL_OPCODES = OP_CLOSE, OP_PING, OP_PONG = 0x08, 0x09, 0x0A

# Close code that are allowed in a close frame.
# Using a list optimizes `code in EXTERNAL_CLOSE_CODES`.
EXTERNAL_CLOSE_CODES = [1000, 1001, 1002, 1003, 1007, 1008, 1009, 1010, 1011]


def apply_mask(data: bytes, mask: bytes) -> bytes:
    """
    Apply masking to the data of a WebSocket message.

    :param data: Data to mask
    :param mask: 4-bytes mask

    """
    if len(mask) != 4:
        raise ValueError("mask must contain 4 bytes")

    return bytes(b ^ m for b, m in zip(data, itertools.cycle(mask)))

def decode(data, mask):
    head1, head2 = struct.unpack("!BB", data[:2])
    data = data[2:]
    fin = True if head1 & 0b10000000 else False
    rsv1 = True if head1 & 0b01000000 else False
    rsv2 = True if head1 & 0b00100000 else False
    rsv3 = True if head1 & 0b00010000 else False
    opcode = head1 & 0b00001111

    if (True if head2 & 0b10000000 else False) != mask:
        raise ValueError("incorrect masking")
    length = head2 & 0b01111111

    print("len=", length)

    if length == 126:
        length, = struct.unpack("!H", data)
        data = data[2:]
        print("len=", length)
    elif length == 127:
        #data = await reader(8)
        length, = struct.unpack("!Q", data)
        data = data[8:]
        print("len=", length)

    if mask:
        #mask_bits = await reader(4)
        mask_bits = data[:4]
        data = data[4:]

    # Read the data.
    #data = await reader(length)
    if mask:
        data = apply_mask(data, mask_bits)


    return (fin, opcode, length, data) #.decode('utf8'))
    #frame = cls(fin, opcode, data, rsv1, rsv2, rsv3)

    #if extensions is None:
    #    extensions = []
    #for extension in reversed(extensions):
    #    frame = extension.decode(frame, max_size=max_size)
#
#    frame.check()
#
#    return frame


def encode(data, mask=False):
    if not isinstance(data, bytes):
        data = data.encode()
    ldata = len(data)
    if ldata > 65536:
        raise ValueError("Only up to 126 supported")
    if ldata < 126:
        return struct.pack('!BB', 0b10000001, ldata) + data
    else:
        return struct.pack('!BBH', 0b10000001, 126, ldata) + data
        #output.write(struct.pack("!BBH", head1, head2 | 126, length))




#def encode(data, mask=False):
#    head1, head2 = struct.unpack("!BB", data[:2])
#    data = data[2:]
#    fin = True if head1 & 0b10000000 else False
#    rsv1 = True if head1 & 0b01000000 else False
#    rsv2 = True if head1 & 0b00100000 else False
#    rsv3 = True if head1 & 0b00010000 else False
#    opcode = head1 & 0b00001111
#
#    if (True if head2 & 0b10000000 else False) != mask:
#        raise ValueError("incorrect masking")
#    length = head2 & 0b01111111
#
#    print("len=", length)
#
#    if length == 126:
#        length, = struct.unpack("!H", data)
#        data = data[2:]
#        print("len=", length)
#    elif length == 127:
#        #data = await reader(8)
#        length, = struct.unpack("!Q", data)
#        data = data[8:]
#        print("len=", length)
#
#    if mask:
#        #mask_bits = await reader(4)
#        mask_bits = data[:4]
#        data = data[4:]
#
#    # Read the data.
#    #data = await reader(length)
#    if mask:
#        data = apply_mask(data, mask_bits)
#





s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(('0.0.0.0', TCP_PORT))
s.listen(1)

state = 0


data_accum = b''

n = 0
pstate = json.dumps({"type":"current_state","state":"currently_presenting","title":"stuff","notes":"坚持 : test","slide_number":-1,"total_slides":5})
#: %s"%(n),"slide_number":-1,"total_slides":5})


conn, addr = s.accept()
while True:

    data = conn.recv(BUFFER_SIZE)
    if data:
        print("Got data: ", data)

#
#        parts = data.split(b'\r\n')
#        print("Parts: ", parts)
#        def splitter(k):
#            sp = k.split(b': ')
#            return sp[0], b': '.join(sp[1:])
#
#        inv = dict(splitter(p) for p in parts)
#
#        key = inv[b'Sec-WebSocket-Key'].decode('utf8')
#        respkey = accept(key)
#
#        res = (b'\r\n'.join([
#            b"HTTP/1.1 101 Switching Protocols",
#            b"Upgrade: websocket",
#            b"Connection: Upgrade",
#            #b"Sec-WebSocket-Accept: %s"%(b"AH2gDkpbU+e0qMGBkN4BiA=="),# respkey.encode()),
#            b"Sec-WebSocket-Accept: %s"%respkey.encode(), #(b"wH2gDkpbU+e0qMGBkN4BiA=="),# respkey.encode()),
#            b"",
#            b""
#        ]))
#
#        print("Sending data: ")
#        print(res )
#
#        conn.send(res)
#
#        conn.send(encode(pstate)) #res[3])) # + b'\r\n' + b'\r\n')
#        conn.send(encode(json.dumps({'type' : 'connected'})))
#        state = 1
#
#    else:
#        data = conn.recv(BUFFER_SIZE)
#        if (data):
#            print("Got data: ", data)
#
#            data_accum += data
#
#            res = (decode(data_accum, True))
#            data_accum = b''
#
#            print ("Got: ", res)
#            print("Responding: ", encode(res[3]))
#            print("Decode: ", decode(encode(res[3]), False))
#
#            if b'next' in res[3]:
#                n += 1
#            else:
#                n -= 1
#
#            #pstate = json.dumps({"type":"current_state","state":"currently_presenting","title":"stuff","notes":"val: %s"%(n),"slide_number":-1,"total_slides":5})
#
#            pstate = json.dumps({"type":"current_state","state":"currently_presenting","title":"stuff","notes":"坚持 : test","slide_number":-1,"total_slides":5})
#            conn.send(encode(pstate)) #res[3])) # + b'\r\n' + b'\r\n')
#
#            #conn.send(encode(res[3])) # + b'\r\n' + b'\r\n')
#
#
#
#            #print(b"Data: " + data)
#            #.decode('utf8'))
#
#
#
#
#
