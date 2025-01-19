import asyncio
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from aiortc.contrib.signaling import TcpSocketSignaling

from networking.data_transmitter import DataTransmitter
import utils.config as config
import utils.error_handler as error_handler


class P2PConnection:
    """
    Establishes and manages peer-to-peer connections, including signaling.
    Delegates media handling to DataTransmitter.
    """
    def __init__(self, signaling_host=config.SIGNALING_SERVER_HOST, signaling_port=config.SIGNALING_SERVER_PORT,
                 local_video=None, local_audio=None):
        self.pc = RTCPeerConnection()
        self.signaling = TcpSocketSignaling(signaling_host, signaling_port)
        self.transmitter = DataTransmitter(self.pc, local_video_track=local_video, local_audio_track=local_audio)
        self.signal_stop = False

    async def start_connection(self, is_initiator):
        """
        Sets up the connection and starts signaling.
        """
        error_handler.log_info("Starting peer-to-peer connection...")
        try:
            if is_initiator:
                await self._create_offer()
            else:
                await self._handle_offer()

            # Start media transmission
            await self.transmitter.send_streams()
            await self.transmitter.receive_streams()

            # @self.pc.on("icecandidate")
            # async def on_icecandidate(candidate):
            #     await self.signaling.send(candidate)

            @self.pc.on("connectionstatechange")
            def broadcast_connection():
                if self.pc.connectionState == 'connected':
                    error_handler.log_info(f"Connection established == Sender: {self.pc.getSenders()} "
                                           f"Receiver: {self.pc.getReceivers()}")
                    # return self.pc
        except Exception as e:
            error_handler.handle_exception(e, context="P2PConnection.setup_connection")

    async def _create_offer(self):
        error_handler.log_info("Creating and sending SDP offer...")
        try:
            offer = await self.pc.createOffer()
            await self.pc.setLocalDescription(offer)
            await self.signaling.send(offer)

            # Handle incoming ICE candidates and answers
            self.signal_stop = True
            await self._handle_signaling()
        except Exception as e:
            error_handler.handle_exception(e, context="P2PConnection._create_offer")

    async def _handle_offer(self):
        error_handler.log_info("Waiting for SDP offer...")
        try:
            offer = await self.signaling.receive()
            await self.pc.setRemoteDescription(offer)

            error_handler.log_info("Sending SDP answer...")
            answer = await self.pc.createAnswer()
            await self.pc.setLocalDescription(answer)
            await self.signaling.send(answer)

            # Handle incoming ICE candidates
            self.signal_stop = True
            await self._handle_signaling()
        except Exception as e:
            error_handler.handle_exception(e, context="P2PConnection._handle_offer")

    async def _handle_signaling(self):
        while self.signal_stop:
            obj = await self.signaling.receive()
            if isinstance(obj, RTCSessionDescription):
                await self.pc.setRemoteDescription(obj)
            elif isinstance(obj, RTCIceCandidate):
                await self.pc.addIceCandidate(obj)

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
