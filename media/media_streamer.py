from media.audio_capture import AudioCapture
from media.video_capture import VideoCapture

import utils.config as config
import utils.error_handler as error_handler


class MediaStreamer:
    """
    Combines audio and video capture into a unified interface.
    Manages starting, stopping, and providing media tracks for transmission.
    """

    def __init__(self, video_source=config.VIDEO_SOURCE, audio_rate=config.AUDIO_SAMPLE_RATE,
                 audio_channels=config.AUDIO_CHANNELS, audio_chunk_size=config.AUDIO_CHUNK_SIZE):
        """
        Initializes media capture components for video and audio.

        Args:
            video_source (int or str): Video source for OpenCV.
            audio_rate (int): Audio sampling rate.
            audio_channels (int): Number of audio channels.
            audio_chunk_size (int): Audio buffer chunk size.
        """
        self.video_capture = VideoCapture(source=video_source)
        self.audio_capture = AudioCapture(rate=audio_rate, channels=audio_channels, chunk_size=audio_chunk_size)
        self.running = False

    def start(self):
        """
        Starts both video and audio capture streams.
        """
        try:
            if self.running:
                error_handler.log_error("Media streams are already running.")
                return
            error_handler.log_info("Starting media streams...")
            self.running = True
            self.video_capture.start()
            self.audio_capture.start()
        except Exception as e:
            error_handler.handle_exception(e, context="MediaStreamer.start")

    def get_video_track(self) -> VideoCapture:
        """
        Provides the video track to be passed to the networking module.

        Returns:
            VideoCapture: An object compatible with the aiortc MediaStreamTrack interface.
        """
        try:
            return self.video_capture
        except Exception as e:
            error_handler.handle_exception(e, context="MediaStreamer.get_video_track")

    def get_audio_track(self) -> AudioCapture:
        """
        Provides the audio track to be passed to the networking module.

        Returns:
            AudioCapture: An object compatible with the aiortc MediaStreamTrack interface.
        """
        try:
            return self.audio_capture
        except Exception as e:
            error_handler.handle_exception(e, context="MediaStreamer.get_audio_track")

    def stop(self):
        """
        Stops both video and audio capture streams.
        """
        try:
            if not self.running:
                error_handler.log_error("Media streams are not running.")
                return
            error_handler.log_info("Stopping media streams...")
            self.video_capture.stop()
            self.audio_capture.stop()
            self.running = False
            error_handler.log_info("Media streams stopped.")
        except Exception as e:
            error_handler.handle_exception(e, context="MediaStreamer.stop")