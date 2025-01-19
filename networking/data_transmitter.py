import asyncio
from aiortc import MediaStreamTrack
from av import AudioFrame, VideoFrame
import time

import utils.threading_utils as thread_utils
import utils.config as config
import utils.error_handler as error_handler


class DataTransmitter:
    """
    Handles encoding, decoding, sending, and receiving of video/audio data streams
    over a peer-to-peer connection.
    """

    def __init__(self, peer_connection, local_video_track=None, local_audio_track=None, video_source=config.VIDEO_SOURCE):
        self.pc = peer_connection
        self.local_video_track = local_video_track
        self.local_audio_track = local_audio_track
        self.video_source = video_source
        self.running = True
        self.video_thread = None
        self.audio_thread = None

    async def send_streams(self):
        """
        Adds local video and audio tracks to the peer connection for transmission.
        """
        try:
            if self.local_video_track:
                error_handler.log_info("Adding local video track to the peer connection")
                self.pc.addTrack(self.local_video_track)

            if self.local_audio_track:
                error_handler.log_info("Adding local audio track to the peer connection")
                self.pc.addTrack(self.local_audio_track)
        except Exception as e:
            error_handler.handle_exception(e, context="data_transmitter.send_streams")

    async def receive_streams(self):
        """
        Handles receiving remote tracks (video/audio) and processes them for playback.
        """
        try:
            @self.pc.on("track")
            def on_track(track):
                error_handler.log_info(f"Receiving track: {track.kind}")
                if track.kind == "video":
                    self.video_thread = thread_utils.run_in_background(self._process_video_track, track)
                elif track.kind == "audio":
                    self.audio_thread = thread_utils.run_in_background(self._process_audio_track, track)
        except Exception as e:
            error_handler.handle_exception(e, context="data_transmitter.receive_streams")

    async def _process_video_track(self, track: MediaStreamTrack):
        """
        Processes incoming video track frames and outputs them.
        """
        error_handler.log_info("Processing video frames from remote peer")
        while self.running:
            try:
                frame = await track.recv()
                if isinstance(frame, VideoFrame):
                    # Here we would render the frame to the GUI (e.g., using OpenCV or Tkinter Canvas)
                    error_handler.log_info(f"Received video frame at {time.time()} with size {frame.width}x{frame.height}")
            except Exception as e:
                error_handler.handle_exception(e, context="data_transmitter._process_video_track")
                break

    async def _process_audio_track(self, track: MediaStreamTrack):
        """
        Processes incoming audio track frames and outputs them.
        """
        error_handler.log_info("Processing audio frames from remote peer")
        while self.running:
            try:
                frame = await track.recv()
                if isinstance(frame, AudioFrame):
                    # Here we would play the audio using PyAudio or a similar library
                    error_handler.log_info(f"Received audio frame at {time.time()}")
            except Exception as e:
                error_handler.handle_exception(e, context="data_transmitter._process_audio_track")
                break

    def stop(self):
        """
        Stops the data transmission by halting tracks and peer connection.
        """
        try:
            error_handler.log_info("Stopping data transmission")
            self.running = False
            thread_utils.stop_thread(self.video_thread)
            thread_utils.stop_thread(self.audio_thread)

            if self.local_video_track:
                self.local_video_track.stop()
            if self.local_audio_track:
                self.local_audio_track.stop()

        except Exception as e:
            error_handler.handle_exception(e, context="data_transmitter.stop")