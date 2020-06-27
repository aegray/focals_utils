import socket
import time
import errno
import queue
import threading
import companion_lib as cl
import os
#aimport sendMessage, BCMessageDecoder

import BC_pb2 as msgs


from socket_manager import BCSocketManager
#from HandshakeResponse_pb2 import HandshakeResponse


chunk_size = 950

serverMACAddress = '00:00:00:1c:1e:b9' #1f:e1:dd:08:3d'
port = 1

class FocalsConnection:
    def __init__(self):
        self.s = None
        self.receiver = None
        self.send_q = []

    def connect(self):
        self.s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        self.s.connect((serverMACAddress,port))
        print("Connected")
        self.s.setblocking(False)

        self.receiver = cl.BCMessageDecoder()

        h = msgs.Handshake()
        h.protocolMinorVersion = 40
        h.protocolMajorVersion = 4

        b = msgs.BlackCoral()
        b.handshake.CopyFrom(h)

        self.s.send(cl.sendMessage(b))

    def clear_q(self):
        msgs = self.send_q[:]
        self.send_q = []
        for x in msgs:
            self.send_raw(x)

    def send_raw(self, msg):
        self.clear_q()
        print("Sending raw: ", msg)
        try:
            self.s.send(msg)
        except BlockingIOError as e:
            print(e)
            self.send_q.append(msg)


    def send(self, msg, extra=None):
        self.clear_q()

        if not isinstance(msg, msgs.BlackCoral):
            msg = cl.make_bc(msg)
        print("Sending msg: ", type(msg).__name__, "(", msg, ")")
        msg = cl.sendMessage(msg, extra=extra)
        try:
            self.s.send(msg)
        except BlockingIOError as e:
            print(e)
            self.send_q.append(msg)


    def close(self):
        if self.s:
            self.s.setblocking(True)
            self.s.shutdown(socket.SHUT_RDWR)
            self.s.close()
            self.s = None

    def process_incoming(self, pubfun=None):
        try:
            r = self.s.recv(chunk_size)
            if pubfun:
                pubfun(r)
            if r:
                print("RECV: ", r)
                for z, b in self.receiver.process(r):
                    yield z, b
        except socket.error as e:
            if e.errno != errno.EWOULDBLOCK:
                if ("temporarily" in str(e)):
                    print(e)
                    pass
                else:
                    raise





conn = FocalsConnection()
conn.connect()




UDP_IP = "127.0.0.1"
UDP_PORT = 32123

socks = BCSocketManager(conn)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock_pub = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


q_input = queue.Queue()
q_raw = queue.Queue()
running = True

def do_quit():
    global running
    global sock
    global sock_pub
    global conn

    running = False

    #sock.close()
    #conn.close()


print("Connected")
#s.setblocking(False)
#h = Handshake()
#h.protocolMinorVersion = 40
#h.protocolMajorVersion = 4
#
#b = BlackCoral()
#b.handshake.CopyFrom(h)
#
#
#f = BCMessageDecoder()
#

print(">")
def handle_command(cmd):
    global running
    cmd = cmd.strip()
    try:
        if cmd == 'help':
            print("""
                pair - StartInputDevicePairing
                exp <name> [key=value ....] - StartExperience with arguments
                sexp <name> - stop experience
                conn 0/1 - set if network is connected
                dummy n - send dummy msg
                tsettings - request templated settings
                features - request features
                caplogs [name] - CaptureLogs (optional reportId)
                screenshot [format] - CaptureScreenshot (optional format)
            """)
        elif cmd.startswith('conn '):
            conn.send(cl.make(msgs.BlackCoral,
                        sync=cl.make(msgs.BlackCoralSync,
                        state=cl.make(msgs.State,
                            isNetReachable=cmd.split()[1] == '1',
                        ))))
        elif cmd == 'pair':
            h = msgs.StartInputDevicePairing()
            b = msgs.BlackCoral()
            b.startInputDevicePairing.CopyFrom(h)
            conn.send(b)
        elif cmd.startswith('dummy '):
            n = cmd.split()[1]
            print("Sending dummy_%s"%(n))
            conn.send(cl.make(msgs.BlackCoral,
                **{ 'dummy_%s'%(n) : cl.make(msgs.DummyEmpty) }
            ))
        elif cmd.startswith("features"):
            conn.send(cl.make(msgs.BlackCoralFeatures,
                featureList = cl.make(msgs.GetFeatureList)
            ))
        elif cmd.startswith("tsettings"):
            conn.send(cl.make(msgs.BlackCoralTemplatedSettings, getSettings = cl.make(msgs.GetSettings)))
        elif cmd.startswith("screenshot"):
            parts = cmd.split()
            if len(parts) > 1:
                conn.send(cl.make(msgs.CaptureScreenshot, fileformat=parts[1]))
            else:
                conn.send(cl.make(msgs.CaptureScreenshot))
        elif cmd.startswith("caplogs"):
            parts = cmd.split()
            if len(parts) > 1:
                conn.send(cl.make(msgs.CaptureLogs, reportId = parts[1]))
            else:
                conn.send(cl.make(msgs.CaptureLogs))

        elif cmd == 'quit':
            do_quit()
            #running = False
            #conn.close()
        elif cmd.startswith("sexp"):
            import re
            #data = """part 1;"this is ; part 2;";'this is ; part 3';part 4;this "is ; part" 5"""
            PATTERN = re.compile(r'''((?:[^\ "']|"[^"]*"|'[^']*')+)''')
            parts = PATTERN.split(cmd)[1::2]

            if len(parts) < 2:
                print("Bad cmd")
            else:
                if parts[1].startswith('"'):
                    parts[1] = parts[1][1:-1]
                conn.send(cl.make(msgs.BlackCoral,
                    stopExperience=cl.make(msgs.StopExperience,
                            name=parts[1],
                        )
                ))

        elif cmd.startswith("exp"):
            import re
            #data = """part 1;"this is ; part 2;";'this is ; part 3';part 4;this "is ; part" 5"""
            PATTERN = re.compile(r'''((?:[^\ "']|"[^"]*"|'[^']*')+)''')
            parts = PATTERN.split(cmd)[1::2]
            if len(parts) < 2:
                print("Bad cmd")
            else:
                if parts[1].startswith('"'):
                    parts[1] = parts[1][1:-1]
                args = [ (k.split('=')[0],  k.split('=')[1]) for k in parts[2:]]
                print(parts[0], parts[1], args)
                conn.send(cl.make(msgs.BlackCoral,
                    startExperience=cl.make(msgs.StartExperience,
                            name=parts[1],
                            parameters=[cl.make(msgs.ParameterEntry, key=k, value=v) for k, v in args]
                        )
                ))

        else:
            print("Invalid command: " + cmd)
    #except KeyboardInterrupt:
    #    raise
    except Exception as e:
        print("Exception handling command: ", e)
        pass

def input_handler():
    global running
    global q_input
    while running:
        r = input()
        q_input.put(r.strip())


def external_cmd_handler():
    global running
    global q_raw
    global sock

    #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #sock.bind((UDP_IP, UDP_PORT))

    while running:
        #scur, _, _ = socket.select.select([sock], [], [])
        #if scur:
        data, addr = sock.recvfrom(chunk_size) # buffer size is 1024 bytes
        q_raw.put(data)

        #else:
        #    time.sleep(0.1)




#def handle_message(msg):
#    if isinstance(msg, msgs.SocketOpen):
#



def pubfun(data):
    sock_pub.sendto(data, ("127.0.0.1", 32124))



t = threading.Thread(target=input_handler)
t.start()

t2 = threading.Thread(target=external_cmd_handler)
t2.start()


while running:
    try:
        while running:
            msgs_done = 0
            did_something = False

            did_something |= socks.service()

            for z, b in conn.process_incoming(pubfun=pubfun):
                did_something = True
                msgs_done += 1
                print("Got Message: ", type(z), z, "buf: ", b)

                socks.process(z, b)



            if msgs_done > 0:
                print("> ",)

            if not q_input.empty():
                did_something = True
                item = q_input.get()
                handle_command(item)

            if not q_raw.empty():
                did_something = True
                item = q_raw.get()
                print("Sending raw data: ", len(item))
                conn.send_raw(item)


            if not did_something:
                time.sleep(0.1)

    except KeyboardInterrupt:
        pass



#conn.close()
#running = False

running = False
sock.close()
conn.close()


print("Waiting input thread")
t.join()
print("Waiting external cmd thread")
t2.join()
print("Closed")

    #text = input()
    #if text == "quit":
    #break
    #s.send(bytes(text, 'UTF-8'))
    #s.close()


