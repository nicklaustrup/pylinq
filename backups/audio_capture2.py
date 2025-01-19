import pyaudio
import threading


class AudioCapture:
    def __init__(self, chunk=1024, format=pyaudio.paInt16, channels=1, rate=44100):
        self.chunk = chunk  # Frames per buffer
        self.format = format  # Audio format
        self.channels = channels  # Mono audio
        self.rate = rate  # Sampling rate
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_capturing = False

    def start_capture(self, callback):
        """Start audio capture and send data to a callback function."""
        self.is_capturing = True
        self.stream = self.audio.open(format=self.format,
                                      channels=self.channels,
                                      rate=self.rate,
                                      input=True,
                                      frames_per_buffer=self.chunk)
        threading.Thread(target=self._capture_loop, args=(callback,), daemon=True).start()

    def _capture_loop(self, callback):
        """Continuously capture audio frames and call the callback."""
        while self.is_capturing:
            try:
                data = self.stream.read(self.chunk)
                callback(data)  # Send audio frames to callback (e.g., for streaming)
            except Exception as e:
                print(f"Error in audio capture: {e}")
                self.stop_capture()

    def stop_capture(self):
        """Stop audio capture and close stream."""
        self.is_capturing = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()
        print("Audio capture stopped.")
