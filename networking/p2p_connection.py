import asyncio
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, RTCConfiguration, RTCIceServer
from aiortc.contrib.signaling import TcpSocketSignaling

from networking.data_transmitter import DataTransmitter
import utils.config as config
import utils.error_handler as error_handler
import json
import websockets


class P2PConnection:
    """
    Establishes and manages peer-to-peer connections, including signaling.
    Delegates media handling to DataTransmitter.
    """
    def __init__(self, signaling_host=config.SIGNALING_SERVER_HOST, signaling_port=config.SIGNALING_SERVER_PORT,
                 local_video=None, local_audio=None):
        self.signaling_host = signaling_host
        self.signaling_port = signaling_port
        ice_servers = [
            RTCIceServer(urls="stun:stun.l.google.com:19302"),  # Use a public STUN server
        ]
        config = RTCConfiguration(iceServers=ice_servers)
        self.pc = RTCPeerConnection(configuration=config)
        self.signaling = TcpSocketSignaling(self.signaling_host, self.signaling_port)
        self.transmitter = DataTransmitter(self.pc, local_video_track=local_video, local_audio_track=local_audio)
        self.signal_stop = False

    async def start_connection(self, is_initiator):
        """
        Sets up the connection and starts signaling.
        """
        error_handler.log_info("Starting peer-to-peer connection...")

        async with websockets.connect(f"ws://{self.signaling_host}:{self.signaling_port}") as websocket:
            @self.pc.on("icecandidate")
            async def on_icecandidate(candidate):
                if candidate:
                    await websocket.send(json.dumps({
                        "candidate": candidate.candidate,
                        "sdpMid": candidate.sdpMid,
                        "sdpMLineIndex": candidate.sdpMLineIndex
                    }))

            @self.pc.on("connectionstatechange")
            def on_connectionstatechange():
                if self.pc.connectionState == 'connected':
                    error_handler.log_info(f"Connection established: Senders: {self.pc.getSenders()}, Receivers: {self.pc.getReceivers()}")

            # Start media transmission
            await self.transmitter.send_streams()
            await self.transmitter.receive_streams()
            
            if is_initiator:
                await self._create_offer(websocket)
            else:
                await self._handle_offer(websocket)

    async def _create_offer(self, websocket):
        error_handler.log_info("Creating and sending SDP offer...")
        try:
            await self.pc.setLocalDescription(await self.pc.createOffer())
            await websocket.send(json.dumps({
                "sdp": self.pc.localDescription.sdp,
                "type": self.pc.localDescription.type
            }))
        except Exception as e:
            error_handler.handle_exception(e, context="P2PConnection._create_offer")

    async def _handle_offer(self, websocket):
        error_handler.log_info("Waiting for SDP offer...")
        try:
            async for message in websocket:
                data = json.loads(message)
                if "sdp" in data:
                    desc = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
                    await self.pc.setRemoteDescription(desc)
                    if desc.type == "offer":
                        await self.pc.setLocalDescription(await self.pc.createAnswer())
                        await websocket.send(json.dumps({
                            "sdp": self.pc.localDescription.sdp,
                            "type": self.pc.localDescription.type
                        }))
                elif "candidate" in data:
                    candidate = RTCIceCandidate(
                        sdpMid=data["sdpMid"],
                        sdpMLineIndex=data["sdpMLineIndex"],
                        candidate=data["candidate"]
                    )
                    await self.pc.addIceCandidate(candidate)
        except Exception as e:
            error_handler.handle_exception(e, context="P2PConnection._handle_offer")

    def stop(self):
        """
        Stops the connection and data transmission.
        """
        error_handler.log_info("Closing peer-to-peer connection...")
        try:
            self.signal_stop = False
            self.transmitter.stop()
            asyncio.run(self.pc.close())
        except Exception as e:
            error_handler.handle_exception(e, context="P2PConnection.stop")
