import asyncio
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.media import MediaPlayer, MediaRecorder

pc = None
local_stream = None

async def handle_candidate(candidate):
    await pc.addIceCandidate(candidate)

async def make_call():
    global pc, local_stream
    pc = RTCPeerConnection()
    local_stream = MediaPlayer('/dev/video0').video
    pc.addTrack(local_stream)

    @pc.on('icecandidate')
    async def on_icecandidate(candidate):
        if candidate:
            signaling.postMessage({'type': 'candidate', 'candidate': candidate})

    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    signaling.postMessage({'type': 'offer', 'sdp': pc.localDescription.sdp})

async def hangup():
    global pc, local_stream
    if pc:
        await pc.close()
        pc = None
    if local_stream:
        await local_stream.stop()
        local_stream = None

async def on_message(e):
    global pc
    if e['type'] == 'candidate':
        await handle_candidate(e['candidate'])
    elif e['type'] == 'ready':
        if pc:
            print('already in call, ignoring')
            return
        await make_call()
    elif e['type'] == 'bye':
        if pc:
            await hangup()
    else:
        print('unhandled', e)

async def start_button_click():
    global local_stream
    local_stream = MediaPlayer('/dev/video0').video
    start_button.disabled = True
    hangup_button.disabled = False
    signaling.postMessage({'type': 'ready'})

async def hangup_button_click():
    await hangup()
    signaling.postMessage({'type': 'bye'})

# Assuming signaling is an object that handles signaling messages
signaling = ...

# Assuming start_button and hangup_button are objects that handle button clicks
start_button = ...
hangup_button = ...

start_button.onclick = start_button_click
hangup_button.onclick = hangup_button_click