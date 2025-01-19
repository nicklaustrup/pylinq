# main.py
import tkinter as tk
import asyncio
from gui.main_window import MainWindow
from media.media_streamer import MediaStreamer
from networking.p2p_connection import P2PConnection
import utils.config as config
import utils.error_handler as error_handler

class LiveStreamingApp:
    """
    Main application class for managing the media and networking layers.
    """

    def __init__(self):
        self.media_streamer = None
        self.p2p_connection = None

    def start_stream(self):
        """
        Starts the media streams and P2P connection.
        """
        try:
            # Initialize media streamer
            self.media_streamer = MediaStreamer(
                video_source=config.VIDEO_SOURCE,
                audio_rate=config.AUDIO_SAMPLE_RATE,
                audio_channels=config.AUDIO_CHANNELS,
                audio_chunk_size=config.AUDIO_CHUNK_SIZE,
            )
            self.media_streamer.start()

            # Initialize P2P connection
            self.p2p_connection = P2PConnection(
                signaling_host=config.SIGNALING_SERVER_HOST,
                signaling_port=config.SIGNALING_SERVER_PORT,
                local_video=self.media_streamer.get_video_track(),
                local_audio=self.media_streamer.get_audio_track(),
            )
            asyncio.ensure_future(self.p2p_connection.start_connection(is_initiator=True))
        except Exception as e:
            error_handler.handle_exception(e, context="start_stream")
            raise

    def stop_stream(self):
        """
        Stops the media streams and P2P connection.
        """
        try:
            if self.media_streamer:
                self.media_streamer.stop()
            if self.p2p_connection:
                self.p2p_connection.stop()
        except Exception as e:
            error_handler.handle_exception(e, context="stop_stream")
            raise

    def get_local_frame(self):
        """
        Retrieves the latest local video frame from the MediaStreamer.

        Returns:
            numpy.ndarray: The most recent video frame.
        """
        if self.media_streamer:
            return self.media_streamer.video_capture.get_frame()
        return None


if __name__ == "__main__":
    app = LiveStreamingApp()

    root = tk.Tk()
    gui = MainWindow(
        root,
        start_stream_callback=app.start_stream,
        stop_stream_callback=app.stop_stream,
        get_local_frame_callback=app.get_local_frame,
    )
    root.mainloop()
