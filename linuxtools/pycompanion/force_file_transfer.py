import socket
import BC_pb2 as msgs
import companion_lib as cl
import time
from google.protobuf.internal.encoder import _VarintBytes
from google.protobuf.internal.decoder import _DecodeVarint32

import google.protobuf.pyext.cpp_message as gpb
import zlib

UDP_SEND=("127.0.0.1", 32123)
UDP_RECV=("127.0.0.1", 32124)


sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock_recv.bind(UDP_RECV)


def crc(data):
    return (zlib.crc32(data) & 0xFFFFFFFF)


avail_path = "1236"
fname = "icon_edit.png"
filedata = open(fname, "rb").read() #"test.wav", "rb").read() #[:200]
checksum = crc(filedata)

print("LEN FILE: ", len(filedata))

def sendmsg(m, extra=None):
    field = type(m).__name__
    if field.startswith("BlackCoral"):
        field = field[len("BlackCoral"):]
    field = field[0].lower() + field[1:]


    print("SENDING: ", type(m).__name__, "(", m, ")", field, extra)
    b = msgs.BlackCoral()
    getattr(b, field).CopyFrom(m)
    msg = cl.sendMessage(b, extra)



    sock_send.sendto(msg, UDP_SEND) #(UDP_IP, UDP_PORT))


#### incoming:
#        message CompanionFileTransfer {
#            optional FileChunkRequest fileChunkRequest = 3;
#                    message FileChunkRequest {
#                        required string id = 1;
#                        required uint32 length = 3;
#                        required uint32 startByte = 2;
#
#                    }
#
#            optional StartFileTransfer startFileTransfer = 1;
#                    message StartFileTransfer {
#                        required string id = 1;
#
#                    }
#
#            optional StopFileTransfer stopFileTransfer = 2;
#                    message StopFileTransfer {
#                        required string id = 1;
#
#                    }
#
#        }
#
#


###################### file trans
#        message BlackCoralFileTransfer {
#            optional FileChunkResponse fileChunkResponse = 2;
#                message FileChunkResponse {
#                    required string id = 1;
#                    required uint32 startByte = 3;
#                    required filetransfer_Status status = 2;
#                }
#
#            optional StartFileTransferResponse startFileTransferResponse = 1;
#                message StartFileTransferResponse {
#                    optional uint32 checksum = 4;
#                    required string id = 1;
#                    optional uint32 length = 3;
#                    required filetransfer_Status status = 2;
#                }
#        }
#
sendmsg(cl.make(msgs.BlackCoralFileTransfer,
            startFileTransferResponse=cl.make(
                msgs.StartFileTransferResponse,
                checksum=checksum,
                id=avail_path,
                length=len(filedata),
                status=0
            )
        ))


receiver = cl.BCMessageDecoder()
while True:
    data, addr = sock_recv.recvfrom(1024) # buffer size is 1024 bytes
    for z, b in receiver.process(data):
        if b:
            print("Got: ", type(z).__name__, z, "buf=", b)
        else:
            print("Got: ", type(z).__name__, z)

        if isinstance(z, msgs.CompanionFileTransfer):
            if z.HasField("fileChunkRequest"):
                fid = z.fileChunkRequest.id

                print("FileChunkRequest, id=", fid)
                if fid == avail_path:
                    print("Sending file chunk: ", z.fileChunkRequest.startByte, z.fileChunkRequest.length)
                    sendmsg(cl.make(msgs.BlackCoralFileTransfer,
                                fileChunkResponse=cl.make(
                                    msgs.FileChunkResponse,
                                    id=fid,
                                    startByte=z.fileChunkRequest.startByte,
                                    status=0
                                )
                            ), filedata[z.fileChunkRequest.startByte:(z.fileChunkRequest.startByte+z.fileChunkRequest.length)])


                #required uint32 length = 3;
                #required uint32 startByte = 2;
                #pass
            elif z.HasField("startFileTransfer"):
                fid = z.startFileTransfer.id
                print("StartFileTransfer, id=", fid)

                if fid == avail_path + "AAAAA":
                    # send back response
                    print("Sending start file transfer, id=", fid)
                    sendmsg(cl.make(msgs.BlackCoralFileTransfer,
                                startFileTransferResponse=cl.make(
                                    msgs.StartFileTransferResponse,
                                    checksum=checksum,
                                    id=fid,
                                    length=len(filedata),
                                    status=0
                                )
                            ))
                pass
            elif z.HasField("stopFileTransfer"):
                fid = z.fileChunkRequest.id
                pass

        else:
            pass







