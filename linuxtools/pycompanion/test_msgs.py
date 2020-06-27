
#from Handshake_pb2 import Handshake
#from HandshakeResponse_pb2 import HandshakeResponse

from BC_pb2 import Handshake, BlackCoral, HandshakeResponse, Companion
from companion_lib import BCMessageDecoder, sendMessage
import BC_pb2 as msgs
import companion_lib as cl
#from google.protobuf.internal.encoder import _VarintBytes
#from google.protobuf.internal.decoder import _DecodeVarint32
#

#
#class FramedReceiver:
#    def __init__(self):
#        self.data = b''
#        self.pending_frame = -1
#
#    def process(self, data):
#        self.data += data
#        while len(self.data) > 0:
#            if self.pending_frame <= 0:
#                self.pending_frame, newpos = _DecodeVarint32(self.data, 0)
#                self.data = self.data[newpos:]
#            sz = len(self.data)
#            if (sz >= self.pending_frame):
#                if self.pending_frame == 0:
#                    print("Received frame of size 0")
#                else:
#                    cur_data = self.data[:self.pending_frame]
#                    self.data = self.data[self.pending_frame:]
#                    self.pending_frame = 0
#                    yield cur_data
#            else:
#                break
#
#
#class MessageReceiver:
#    def __init__(self):
#        self.framer = FramedReceiver()
#
#    def process(self, data):
#        for m in self.framer.process(data):
#            lval, newpos = _DecodeVarint32(m, 0)
#            encdata = m[newpos:(newpos+lval)]
#            yield encdata
#
#
#class BCMessageDecoder:
#    def __init__(self):
#        self.recv = MessageReceiver()
#
#    def process(self, data):
#        for m in self.recv.process(data):
#            h = Handshake()
#            h.ParseFromString(m)
#            print(h)
#
#
#def _sendFramed(data):
#    lval = _VarintBytes(len(data))
#    return lval + data
#
#def sendMessage(msg):
#    data = msg.SerializeToString()
#    lval = _VarintBytes(len(data))
#    return _sendFramed(lval + data)
#

#
#def decodeFramedMessage(data):
#    lval, newpos = _DecodeVarint32(data, 0)
#    lval2, newpos = _DecodeVarint32
#    h = Handshake()
#    h.ParseFromString(data[newpos:])
#    print(lval, h)
#
#h = Handshake()
#h.protocolMajorVersion = 4
#h.protocolMinorVersion = 40
#
#b = BlackCoral()
#b.handshake.CopyFrom(h)
#
#h = HandshakeResponse()
#h.protocolMajorVersion = 4
#h.protocolMinorVersion = 40
#h.requiredProtocolMajorVersion = 4
#h.requiredProtocolMinorVersion = 40
#h.result = 0
#h.softwareVersion = "HELLO"
#
#b = Companion()
#b.handshakeResponse.CopyFrom(h)
#
#
#
##
##def dump_object(obj):
##    for descriptor in obj.DESCRIPTOR.fields:
##        #value = getattr(obj, descriptor.name)
##        if descriptor.type == descriptor.TYPE_MESSAGE:
##
##            print(descriptor.name, obj.HasField(descriptor.name))
###
###            if descriptor.label == descriptor.LABEL_REPEATED:
###                print("   List")
###                #map(dump_object, value)
###            else:
###                print("   value")
###                #dump_object(value)
###        elif descriptor.type == descriptor.TYPE_ENUM:
###            print("   enum")
###            #enum_name = descriptor.enum_type.values[value].name
###            #print "%s: %s" % (descriptor.full_name, enum_name)
###        else:
###            print("   other")
###            #print "%s: %s" % (descriptor.full_name, value)
###    #print("Field: ", d)
###
##dump_object(b)
##
#f = BCMessageDecoder()
#msg = sendMessage(b)
#
#for z in f.process(msg):
#    print(z)
#
##decodeMessage(msg)
#
#

print(cl.make(msgs.BlackCoralFileTransfer,
                                startFileTransferResponse=cl.make(
                                    msgs.StartFileTransferResponse,
                                    checksum=123,
                                    id="abcd",
                                    length=12, #len(filedata),
                                    status=0
                                )
                            ))
