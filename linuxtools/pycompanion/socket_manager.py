import socket
import select
import errno

import companion_lib as cl
import BC_pb2 as msgs

intercept = False

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
            return True
        elif isinstance(z, msgs.SocketOpen):
            self.sockets.open(z.streamId, z.host, z.port)
            return True
        elif isinstance(z, msgs.SocketClose):
            self.sockets.close(z.streamId)
            self.conn.send(cl.make(msgs.SocketCloseResponse,
                    status = 0,
                    streamId = z.streamId))
            return True
        elif isinstance(z, msgs.SocketDataChunk):
            self.sockets.send(z.streamId, b)
            return True
        elif isinstance(z, msgs.SocketError):
            self.sockets.close(z.streamId)
            return True
        else:
            return False

    def service(self):
        did_something = False
        for sid, connected, data, err in self.sockets.service():
            did_something = True
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
        return did_something
