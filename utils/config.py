"""
Centralized configuration settings for Linq'd livestream application.
Contains default parameters for video, audio, and networking modules.
"""

# Video Configuration
VIDEO_SOURCE = 0  # Default video source (0 = primary webcam)
VIDEO_FRAME_RATE = 30  # Frames per second
VIDEO_RESOLUTION = (640, 480)  # Default resolution: 640x480
VIDEO_WIDTH = 320
VIDEO_HEIGHT = 240

# Audio Configuration
AUDIO_SAMPLE_RATE = 44100  # Audio sample rate (Hz)
AUDIO_CHANNELS = 1  # Mono audio
AUDIO_CHUNK_SIZE = 1024  # Buffer chunk size for PyAudio

# Networking Configuration
SIGNALING_SERVER_HOST = "127.0.0.1"  # Default signaling server address
SIGNALING_SERVER_PORT = 9999  # Default signaling server port

# Logging Configuration
LOGGING_LEVEL = "INFO"  # Logging levels: DEBUG, INFO, WARNING, ERROR