import os
import socket
import random

TCP_PORT = 4343
BUFFER_SIZE = 1024*20

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(('0.0.0.0', TCP_PORT))
s.listen(1)

while True:
    conn, addr = s.accept()
    for i in range(500):
        nb = random.randint(5, 2500)

        buf = os.urandom(nb)

        print(f'testing: iter={i} : nb={nb}')
        conn.send(buf)

        rembuf = buf[:]

        while rembuf:
            data = conn.recv(BUFFER_SIZE)


            print(f"Got: {len(data)}")

            if len(data) < len(rembuf):
                curbuf = rembuf[:len(data)]
                rembuf = rembuf[len(data):]
                assert len(data) == len(curbuf), "Lens didn't match"
                assert data == curbuf, "data didn't match"

                print("REM: ", len(rembuf))
            else:
                assert len(data) == len(rembuf), "Lens didn't match"
                assert data == rembuf, "data didn't match"
                rembuf = None
            #else:
            #    rembuf = None

        if not data:
            break


    conn.close()


