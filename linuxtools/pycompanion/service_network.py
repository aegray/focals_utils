import socket
import errno

import select
import BC_pb2 as msgs
import companion_lib as cl
import time
from google.protobuf.internal.encoder import _VarintBytes
from google.protobuf.internal.decoder import _DecodeVarint32

import google.protobuf.pyext.cpp_message as gpb
import zlib

UDP_SEND=("127.0.0.1", 32123)
UDP_RECV=("127.0.0.1", 32124)

intercept = False
do_logging = True

sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock_recv.bind(UDP_RECV)
sock_recv.setblocking(False)



class SocketManager:
    def __init__(self):
        self.opening = {}
        self.socks = {}

    def open(self, streamid, host, port):
        print("Opening: ", streamid, host, port)
        newsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        newsock.setblocking(False)
        err = newsock.connect_ex((host, port))
        self.opening[streamid] = newsock

    def send(self, streamid, data):
        if streamid in self.socks:
            self.socks[streamid].send(data)
            return True
        else:
            return False


    def close(self, streamid):
        if streamid in self.socks:
            self.socks[streamid].close()
            del self.socks[streamid]
            return True
        return False


    def service(self):
        opened = list(self.socks.items())
        opening = list(self.opening.items())

        opened_s = [x[1] for x in opened]
        opening_s = [x[1] for x in opening]

        #print("checking: ", opened_s, opening_s)

        #ready_read, ready_write, ready_except = select.select(opened_s, opening_s, opened_s + opening_s, 0)
        ready_read, ready_write, ready_except = select.select(opened_s, opening_s, opened_s + opening_s, 0)

        def getsockid(s, c):
            match = [x[0] for x in c if x[1] == s]
            assert len(match) == 1
            return match[0]

        errids = set()

        processed = set()

        #print("Ready: ", ready_read, ready_write, ready_except)
        for x in ready_except + ready_write:
            sid = getsockid(x, opened + opening)
            if sid not in processed:
                #errids.add(sid)
                processed.add(sid)
                errv = x.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                if errv == 0:
                    assert sid in self.opening
                    del self.opening[sid]
                    self.socks[sid] = x
                    yield (sid, True, None, None)
                else:
                    print("EXCEPTION ON SOCK: ", sid, errno.errorcode[errv])
                    if sid in self.opening:
                        yield (sid, False, None, errv)
                        del self.opening[sid]

                    if sid in self.socks:
                        yield (sid, True, None, errv)
                        del self.socks[sid]


        for x in ready_read:
            sid = getsockid(x, opened)
            try:
                data = x.recv(900)
                if data:
                    yield (sid, False, data, None)
            except Exception as e:
                print(e)
                del self.socks[sid]
                yield (sid, False, None, 104)


class BCSocketManager:
    def __init__(self, conn):
        self.sockets = SocketManager()
        self.conn = conn

    def process(self, z, b):
        if isinstance(z, msgs.GetHostByName):
            if not intercept:
                self.conn.send(cl.make(msgs.GetHostByNameResponse,
                        host=socket.gethostbyname(z.name), #"10.0.0.251",
                        name=z.name,
                        status=0
                    ))
            else:
                self.conn.send(cl.make(msgs.GetHostByNameResponse,
                        #host="10.0.0.148", #251",
                        host="10.0.0.148", #251",
                        name=z.name,
                        status=0
                    ))
        elif isinstance(z, msgs.SocketOpen):
            self.sockets.open(z.streamId, z.host, z.port)
        elif isinstance(z, msgs.SocketClose):
            self.sockets.close(z.streamId)
            self.conn.send(cl.make(msgs.SocketCloseResponse,
                    status = 0,
                    streamId = z.streamId))
        elif isinstance(z, msgs.SocketDataChunk):
            self.sockets.send(z.streamId, b)
        elif isinstance(z, msgs.SocketError):
            self.sockets.close(z.streamId)
        else:
            pass

    def service(self):
        for sid, connected, data, err in self.sockets.service():
            if data:
                self.conn.send(cl.make(msgs.SocketDataChunk, streamId = sid), extra=data)
            elif err:
                if connected:
                    self.conn.send(cl.make(msgs.SocketError,
                        streamId = sid,
                        errorCode = err
                    ))
                else:
                    self.conn.send(cl.make(msgs.SocketOpenResponse,
                        status = 1,
                        streamId = sid,
                        errorCode = err
                    ))
            elif connected:
                self.conn.send(cl.make(msgs.SocketOpenResponse,
                    status = 0,
                    streamId = sid
                ))



def sendmsg(m, extra=None):
    print("Sending: ", type(m).__name__, "(", m, ")", extra)
    return cl.send_to_socket(sock_send, m, extra=extra)

receiver = cl.BCMessageDecoder()
sock_handler = SocketManager()

while True:
    did_something = False
    try:
        res = sock_recv.recvfrom(1024) # buffer size is 1024 bytes
        if res:
            did_something = True
            data, _ = res
            for z, b in receiver.process(data):
                if b:
                    print("Got: ", type(z).__name__, z, "buf=", b)
                else:
                    print("Got: ", type(z).__name__, z)

                if isinstance(z, msgs.GetHostByName):
                    if not intercept:
                        sendmsg(cl.make(msgs.GetHostByNameResponse,
                                host=socket.gethostbyname(z.name), #"10.0.0.251",
                                name=z.name,
                                status=0
                            ))
                    else:
                        sendmsg(cl.make(msgs.GetHostByNameResponse,
                                #host="10.0.0.148", #251",
                                host="10.0.0.148", #251",
                                name=z.name,
                                status=0
                            ))
                elif isinstance(z, msgs.SocketOpen):
                    sock_handler.open(z.streamId, z.host, z.port)
                elif isinstance(z, msgs.SocketClose):
                    sock_handler.close(z.streamId)
                    sendmsg(cl.make(msgs.SocketCloseResponse,
                            status = 0,
                            streamId = z.streamId))
                elif isinstance(z, msgs.SocketDataChunk):
                    sock_handler.send(z.streamId, b)
                elif isinstance(z, msgs.SocketError):
                    sock_handler.close(z.streamId)
    except Exception as e:
        pass

    for sid, connected, data, err in sock_handler.service():
        did_something = True
        if data:
            sendmsg(cl.make(msgs.SocketDataChunk, streamId = sid), extra=data)
        elif err:
            if connected:
                sendmsg(cl.make(msgs.SocketError,
                    streamId = sid,
                    errorCode = err
                ))
            else:
                sendmsg(cl.make(msgs.SocketOpenResponse,
                    status = 1,
                    streamId = sid,
                    errorCode = err
                ))
        elif connected:
            sendmsg(cl.make(msgs.SocketOpenResponse,
                status = 0,
                streamId = sid
            ))

    if not did_something:
        time.sleep(0.1)



