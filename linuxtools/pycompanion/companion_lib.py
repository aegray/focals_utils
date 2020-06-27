#from Handshake_pb2 import Handshake
#from HandshakeResponse_pb2 import HandshakeResponse

import BC_pb2 as comp

from google.protobuf.internal.encoder import _VarintBytes
from google.protobuf.internal.decoder import _DecodeVarint32
import google.protobuf.pyext.cpp_message as gpb

UDP_SEND=("127.0.0.1", 32123)
UDP_RECV=("127.0.0.1", 32124)

class FramedReceiver:
    def __init__(self):
        self.data = b''
        self.pending_frame = -1

    def process(self, data):
        self.data += data
        while len(self.data) > 0:
            if self.pending_frame <= 0:
                self.pending_frame, newpos = _DecodeVarint32(self.data, 0)
                self.data = self.data[newpos:]
            sz = len(self.data)
            if (sz >= self.pending_frame):
                if self.pending_frame == 0:
                    print("Received frame of size 0")
                else:
                    cur_data = self.data[:self.pending_frame]
                    self.data = self.data[self.pending_frame:]
                    self.pending_frame = 0
                    yield cur_data
            else:
                break


class MessageReceiver:
    def __init__(self):
        self.framer = FramedReceiver()

    def process(self, data):
        for m in self.framer.process(data):
            lval, newpos = _DecodeVarint32(m, 0)
            encdata = m[newpos:(newpos+lval)]
            yield encdata, m[(newpos+lval):]


class BCMessageDecoder:
    def __init__(self):
        self.recv = MessageReceiver()

    def process(self, data):
        for m, b in self.recv.process(data):
            c = comp.Companion()
            c.ParseFromString(m)
            for descriptor in c.DESCRIPTOR.fields:
                if descriptor.type == descriptor.TYPE_MESSAGE:
                    if c.HasField(descriptor.name):
                        yield getattr(c, descriptor.name), b
                    #print(descriptor.name, obj.HasField(descriptor.name))





            #h = Handshake()
            #h.ParseFromString(m)
            #print(h)


def _sendFramed(data):
    lval = _VarintBytes(len(data))
    return lval + data

def sendMessage(msg, extra=None):
    data = msg.SerializeToString()
    lval = _VarintBytes(len(data))
    data = lval + data
    if extra:
        data = data + extra

    return _sendFramed(data)


def make(c, **kw):
    m = c()
    for k, v in kw.items():
        if isinstance(v, list):
            getattr(m, k).extend(v)
        elif isinstance(type(v), gpb.GeneratedProtocolMessageType):
            getattr(m, k).CopyFrom(v)
        else:
            setattr(m, k, v)

    return m

def make_bc(m):
    field = type(m).__name__
    if field.startswith("BlackCoral"):
        field = field[len("BlackCoral"):]
    field = field[0].lower() + field[1:]

    b = comp.BlackCoral()
    getattr(b, field).CopyFrom(m)
    return b



def send_to_socket(sock, m, extra=None):
    b = make_bc(m)
    msg = sendMessage(b, extra)

    #sock_send.sendto(msg, UDP_SEND) #(UDP_IP, UDP_PORT))
    onind = 0

    while onind < len(msg):
        endind = min(len(msg), onind+1000)
        cur = msg[onind:endind]
        #endind
        print("Sending: ", len(cur), " startoff=", onind)
        onind += 1000
        sock.sendto(cur, UDP_SEND) #(UDP_IP, UDP_PORT))

#lval + data)


##
##def decodeFramedMessage(data):
##    lval, newpos = _DecodeVarint32(data, 0)
##    lval2, newpos = _DecodeVarint32
##    h = Handshake()
##    h.ParseFromString(data[newpos:])
##    print(lval, h)
##
#h = Handshake()
#h.protocolMajorVersion = 4
#h.protocolMinorVersion = 40
#
#f = BCMessageDecoder()
#msg = sendMessage(h)
#
#f.process(msg)
##decodeMessage(msg)
#
#
#
#
#
#
