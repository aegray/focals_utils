
import time
import asyncio
import websockets
import base64

imgdata = None

# write bin data
with open("konacast_data.txt", "rb") as fin:
    imgdata = fin.read()

async def reader(ws):
    with open("output.txt", "w") as fout:
        while True:
            data = await ws.recv()
            fout.write('\n\n')
            fout.write(data)
            fout.flush()




async def writer(ws):
    onind = 0
    while onind < 5:
        time.sleep(1)
        await ws.send('{"%s%s%s"}') #'{"abc": "123"}\r\n\r\n') #\x001'*(220*220*3)) #{\\"width: 220, "height": 220, "data": "" }')
        #await ws.send('{"abc": "123"}\r\n\r\n') #\x001'*(220*220*3)) #{\\"width: 220, "height": 220, "data": "" }')
        #%s"}'%(base64.b64encode(b'\0'*(220*220*4))))
        #await ws.send('{"width": 220, "height": 220, "data": "%s"}'%(base64.b64encode(b'\0'*(220*220*4))))
        #await ws.send(imgdata) #base64.b64encode(b'\0'*(220*220*4))))
        #imgdata)

        #        b"{\"type\": \"frame\", \"data\": \"" + imgdata + b"\"}") #[:10]) #"{\"type\": \"frame\"}")
        onind += 1



#
#
#
#            #TESTING")
#            #imgdata)
#
#
#        while True:
#            name = await ws.recv()
#            print(name)
#            fout.write('\n\n')
#            fout.write(name)
#



async def hello(ws, path):
    onind = 0

    print("Connected")
    a = await asyncio.gather(reader(ws), writer(ws))

    print("DONE")

#
#        while onind < 5:
#            name = await ws.recv()
#            print(name)
#            fout.write('\n\n')
#            fout.write(name)
#
#            onind += 1
#
#            await ws.send("{\"type\": \"frame\"}")
#            #TESTING")
#            #imgdata)
#
#
#        while True:
#            name = await ws.recv()
#            print(name)
#            fout.write('\n\n')
#            fout.write(name)
#
#
#
#
#
#            #print(f"< {name}")
#

start_server = websockets.serve(hello, "0.0.0.0", 8002)


asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()



