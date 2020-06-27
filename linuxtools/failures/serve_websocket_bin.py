

import asyncio
import websockets



async def hello(ws, path):

    with open("output.txt", "wb") as fout:
        print("Connected")
        while True:
            name = await ws.recv()

            fout.write(b'\n\n')
            fout.write(("Got: %s"%(len(name))).encode())
            fout.write(b'\n\n')
            fout.write(name)

            #print(f"< {name}")


start_server = websockets.serve(hello, "0.0.0.0", 8002)


asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()



