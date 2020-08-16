#!/usr/bin/env python

import struct
import socket

TCP_IP = '0.0.0.0'
TCP_PORT = 31483
BUFFER_SIZE = 8196  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)


try:

    conn, addr = s.accept()
    print ('Connection address:', addr)
    while 1:
        data = None

        while not data:
            data = conn.recv(BUFFER_SIZE)

        print(data.decode('utf8'))
#
#        print("> ", end='')
#        data = input()
#
#        need_resp = False
#
#        parts = data.split(' ')
#        if len(parts) == 1 and parts[0] == 'f':
#            parts = ['s', 'cmd_and_control', '/data/app/cmd_and_control_new']
#            #parts = ['s', 'cmd_and_control', '/data/app/cmd_and_control']
#
#        if len(parts) == 1 and parts[0] == 'r':
#            parts = ['c', 'killall', 'cmd_and_control']
#            #, ';', '/data/app/cmd_and_control']
#            #parts = ['c', 'killall', 'cmd_and_control', ';', '/data/app/cmd_and_control']
#
#        if len(parts) > 1 and parts[0] == 's':
#            if len(parts) == 3:
#                need_resp = True
#                fname = parts[1].encode('ascii')
#                fnameto = parts[2].encode('ascii')
#
#                print("Sending: %s -> %s"%(parts[1], parts[2]))
#
#                conn.send(b's' + struct.pack('I', len(fnameto)) + fnameto)
#                data = open(fname, 'rb').read()
#                conn.send(struct.pack("I", len(data)) + data)
#
#            else:
#                print("ERROR")
#
#        elif len(parts) > 1 and parts[0] == 'c':
#            need_resp = True
#            print("PARTS: ", parts)
#            cmd = (' '.join(parts[1:])).encode('ascii')
#            print("pack: ", struct.pack("<I", len(cmd)))
#            conn.send(b'c' + struct.pack("<I", len(cmd)) + cmd)
#        else:
#            print("ERROR bad cmd")
#
#
#        if need_resp:
#            data = None
#
#            while not data:
#                data = conn.recv(BUFFER_SIZE)
#
#
#            print("Got ack: ", data)
#
#
#        #print("Sending: ", data)
#        #conn.send(data.encode('ascii'))
#
#    #    data = conn.recv(BUFFER_SIZE)
#    #    if not data: break
#    #    print "received data:", data
#    #    conn.send(data)  # echo


except KeyboardInterrupt:
    pass

conn.close()
