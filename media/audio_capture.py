from collections import deque
from aiortc.mediastreams import AudioStreamTrack
import pyaudio

import utils.threading_utils as threading_utils
import utils.config as config
import utils.error_handler as error_handler


class AudioCapture(AudioStreamTrack):
    """
    Captures audio input using PyAudio and provides chunks of audio data for processing.
    """

    def __init__(self, rate=config.AUDIO_SAMPLE_RATE, channels=config.AUDIO_CHANNELS, chunk_size=config.AUDIO_CHUNK_SIZE):
        """
        Initializes the audio capture settings.

        Args:
            rate (int): Sampling rate for audio capture.
            channels (int): Number of audio channels.
            chunk_size (int): Size of each audio buffer chunk.
        """
        super().__init__()
        self.rate = rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.audio_interface = pyaudio.PyAudio()
        self.stream = None
        self.running = False
        self.thread = None
        self.audio_buffer = deque()  # Buffer to store captured audio chunks

    def start(self):
        """
        Starts the audio capture stream and recording thread.
        """
        if self.running:
            error_handler.log_error("Audio capture is already running.")
            return

        error_handler.log_info("Starting audio capture...")
        self.stream = self.audio_interface.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size,
        )
        self.running = True
        self.thread = threading_utils.run_in_background(self._capture_audio)

    def _capture_audio(self):
        """
        Continuously captures audio chunks and stores them in the buffer.
        """
        error_handler.log_info("Attempting to capture audio chunks...")
        while self.running:
            try:
                audio_chunk = self.stream.read(self.chunk_size, exception_on_overflow=False)
                self.audio_buffer.append(audio_chunk)
            except Exception as e:
                error_handler.handle_exception(e, context="AudioCapture._capture_audio")
                self.stop()

    def get_audio_chunk(self):
        """
        Retrieves the latest audio chunk from the buffer, if available.

        Returns:
            bytes: The most recent audio chunk.
        """
        try:
            if self.audio_buffer:
                return self.audio_buffer.popleft()
            return None
        except Exception as e:
            error_handler.handle_exception(e, context="AudioCapture.get_audio_chunk")

    def stop(self):
        """
        Stops the audio capture and closes the stream.
        """
        try:
            if not self.running:
                error_handler.log_warning("Audio capture is not running.")
                return

            error_handler.log_info("Stopping audio capture...")
            self.running = False
            threading_utils.stop_thread(self.thread)
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            self.audio_interface.terminate()
            error_handler.log_info("Audio capture stopped.")
        except Exception as e:
            error_handler.handle_exception(e, context="AudioCapture.stop")