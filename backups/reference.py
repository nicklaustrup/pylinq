from google.cloud import firestore
import asyncio
import websockets
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
import cv2

configuration = {
    'iceServers': [
        {
            'urls': [
                'stun:stun1.l.google.com:19302',
                'stun:stun2.l.google.com:19302',
            ],
        },
    ],
    'iceCandidatePoolSize': 10,
}

peer_connection = None
local_stream = None
remote_stream = None
room_dialog = None
room_id = None


def init():
    # GUI event listeners will be different in Python
    pass


async def create_room():
    global peer_connection, room_id
    db = firestore.Client()
    room_ref = db.collection('rooms').document()

    print(f'Create PeerConnection with configuration: {configuration}')
    peer_connection = RTCPeerConnection(configuration)

    register_peer_connection_listeners()

    for track in local_stream.get_tracks():
        peer_connection.addTrack(track)

    caller_candidates_collection = room_ref.collection('callerCandidates')

    @peer_connection.on('icecandidate')
    async def on_icecandidate(event):
        if not event.candidate:
            print('Got final candidate!')
            return
        print(f'Got candidate: {event.candidate}')
        caller_candidates_collection.add(event.candidate.toJSON())

    offer = await peer_connection.createOffer()
    await peer_connection.setLocalDescription(offer)
    print(f'Created offer: {offer}')

    room_with_offer = {'offer': {'type': offer.type, 'sdp': offer.sdp}}
    await room_ref.set(room_with_offer)
    room_id = room_ref.id
    print(f'New room created with SDP offer. Room ID: {room_ref.id}')

    @peer_connection.on('track')
    def on_track(event):
        print(f'Got remote track: {event.streams[0]}')
        for track in event.streams[0].get_tracks():
            print(f'Add a track to the remoteStream: {track}')
            remote_stream.addTrack(track)

    async def on_snapshot(snapshot, changes, read_time):
        data = snapshot.to_dict()
        if not peer_connection.currentRemoteDescription and data and data.get('answer'):
            print(f'Got remote description: {data["answer"]}')
            rtc_session_description = RTCSessionDescription(data['answer']['sdp'], data['answer']['type'])
            await peer_connection.setRemoteDescription(rtc_session_description)

    room_ref.on_snapshot(on_snapshot)

    async def on_callee_candidates_snapshot(snapshot, changes, read_time):
        for change in changes:
            if change.type.name == 'ADDED':
                data = change.document.to_dict()
                print(f'Got new remote ICE candidate: {data}')
                await peer_connection.addIceCandidate(data)

    room_ref.collection('calleeCandidates').on_snapshot(on_callee_candidates_snapshot)


async def join_room():
    global room_id
    # GUI event listeners will be different in Python
    pass


async def join_room_by_id(room_id):
    global peer_connection
    db = firestore.Client()
    room_ref = db.collection('rooms').document(room_id)
    room_snapshot = await room_ref.get()
    print(f'Got room: {room_snapshot.exists}')

    if room_snapshot.exists:
        print(f'Create PeerConnection with configuration: {configuration}')
        peer_connection = RTCPeerConnection(configuration)
        register_peer_connection_listeners()
        for track in local_stream.get_tracks():
            peer_connection.addTrack(track)

        callee_candidates_collection = room_ref.collection('calleeCandidates')

        @peer_connection.on('icecandidate')
        async def on_icecandidate(event):
            if not event.candidate:
                print('Got final candidate!')
                return
            print(f'Got candidate: {event.candidate}')
            callee_candidates_collection.add(event.candidate.toJSON())

        @peer_connection.on('track')
        def on_track(event):
            print(f'Got remote track: {event.streams[0]}')
            for track in event.streams[0].get_tracks():
                print(f'Add a track to the remoteStream: {track}')
                remote_stream.addTrack(track)

        offer = room_snapshot.to_dict().get('offer')
        print(f'Got offer: {offer}')
        await peer_connection.setRemoteDescription(RTCSessionDescription(offer['sdp'], offer['type']))
        answer = await peer_connection.createAnswer()
        print(f'Created answer: {answer}')
        await peer_connection.setLocalDescription(answer)

        room_with_answer = {'answer': {'type': answer.type, 'sdp': answer.sdp}}
        await room_ref.update(room_with_answer)

        async def on_caller_candidates_snapshot(snapshot, changes, read_time):
            for change in changes:
                if change.type.name == 'ADDED':
                    data = change.document.to_dict()
                    print(f'Got new remote ICE candidate: {data}')
                    await peer_connection.addIceCandidate(data)

        room_ref.collection('callerCandidates').on_snapshot(on_caller_candidates_snapshot)


async def open_user_media():
    global local_stream, remote_stream
    local_stream = cv2.VideoCapture(0)
    remote_stream = MediaStreamTrack()

    print(f'Stream: {local_stream}')
    # GUI element updates will be different in Python


async def hang_up():
    global room_id
    for track in local_stream.get_tracks():
        track.stop()

    if remote_stream:
        for track in remote_stream.get_tracks():
            track.stop()

    if peer_connection:
        peer_connection.close()

    # GUI element updates will be different in Python

    if room_id:
        db = firestore.Client()
        room_ref = db.collection('rooms').document(room_id)
        callee_candidates = await room_ref.collection('calleeCandidates').get()
        for candidate in callee_candidates:
            await candidate.reference.delete()
        caller_candidates = await room_ref.collection('callerCandidates').get()
        for candidate in caller_candidates:
            await candidate.reference.delete()
        await room_ref.delete()

    # GUI reload will be different in Python


def register_peer_connection_listeners():
    @peer_connection.on('icegatheringstatechange')
    def on_icegatheringstatechange():
        print(f'ICE gathering state changed: {peer_connection.iceGatheringState}')

    @peer_connection.on('connectionstatechange')
    def on_connectionstatechange():
        print(f'Connection state change: {peer_connection.connectionState}')

    @peer_connection.on('signalingstatechange')
    def on_signalingstatechange():
        print(f'Signaling state change: {peer_connection.signalingState}')

    @peer_connection.on('iceconnectionstatechange')
    def on_iceconnectionstatechange():
        print(f'ICE connection state change: {peer_connection.iceConnectionState}')


init()
