
import asyncio
import websockets
import requests
import json
from aioconsole import ainput

onind = 0
state = {
        'state' : '',
        'title' : '',
        'notes' : '',
        'slide_number' : 0,
        'total_slides' : 0
    }


def slide_data(notes):
    return json.dumps({
            'type' : 'current_state',
            'data' : {
                'state' : 'currently_presenting',
                'title' : 'stuff',
                'notes' : notes,
                'slide_number' : -1,
                'total_slides' : 5
            }
        })



async def send_slide(ws, n):
    data = slide_data('<font size=23>去商店: %s<br><br>HELLO</font>'%(n))
    print("Sending: ", data)
    await ws.send(data) #slide_data('slide: %s'%(n)))



async def handle(ws, msg):
    global onind
    msg = json.loads(msg)
    print("GOT: ", msg, " / ", type(msg))
    msgt = msg.get('type', None)
    if msgt == 'connected':
        print("Got conneected, sending slide: ")
        # connected
        #if (onind == 0):
        onind = 1
        await send_slide(ws, onind)

    elif msgt == 'next_slide':
        onind += 1
        await send_slide(ws, onind)

    elif msgt == 'previous_slide':
        onind -= 1
        await send_slide(ws, onind)


#GOT:  {'type': 'current_state', 'state': '', 'title': '', 'notes': '', 'slide_number': 0, 'total_slides': 0}  /  <class 'dict'>
#GOT:  {'type': 'connected'}  /  <class 'dict'>
#Got conneected, sending slide:
#Sending:  {"type": "current_state", "data": {"state": "currently_presenting", "title": "stuff", "notes": "slide: 2", "slide_number": 1, "total_slides": 5}}
#GOT:  {'type': 'next_slide'}  /  <class 'dict'>
#GOT:  {'type': 'previous_slide'}  /  <class 'dict'>
#


    #elif msgt == 'next_slide':
    #    return


async def next_msg(ws):
    val = await ws.recv()
    return (0, val)


async def next_input():
    val = await ainput()
    return (1, val)

#{"type":"current_state","state":"","title":"","notes":"","slide_number":0,"total_slides":0}  /  <class 'str'>

async def hello(pcode):
    global onind
    uri = "ws://north-teleprompter.herokuapp.com:80/?presentation_code=%s&role=browser_extension"%(pcode)

    async with websockets.connect(uri) as s:

        while onind < 10:
            #await s.send(stuff)
            val = await next_msg(s) #await asyncio.wait([next_msg(s), next_input()], return_when=asyncio.FIRST_COMPLETED)

            if val[0] == 0:
                await handle(s, val[1])

            elif val[0] == 1:
                await send_slide(s, onind)





def get_presentation_code():
    uri = "http://north-teleprompter.herokuapp.com/v1/presentation"

    resp = requests.post(url = uri)
    return resp.json()['accessCode']

def code_as_letters(code):
    return str(list(chr(ord(x)-ord('0')+ord('A')) for x in code))


#pcode = '212'
pcode = '321'
#pcode = get_presentation_code()
print(pcode)
print(''.join(code_as_letters(pcode)))



#hello(pcode)


asyncio.get_event_loop().run_until_complete(hello(pcode))
