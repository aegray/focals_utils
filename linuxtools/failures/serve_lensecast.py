

import asyncio
import websockets
import struct


async def hello(ws, path):

    with open("output.txt", "ab") as fout:
        print("Connected")
        while True:
            name = await ws.recv()

            fout.write(b'\n\n')
            fout.write(("Got: %s"%(len(name))).encode())
            fout.write(b'\n\n')
            fout.write(name)

            await ws.send('{"width": 220,"height": 220,"frameInterval": 140,"lossless": true}')



            #print(f"< {name}")


start_server = websockets.serve(hello, "0.0.0.0", 8002)


asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()



