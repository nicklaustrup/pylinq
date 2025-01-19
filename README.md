# live_stream_app/
# │
# ├── main.py                         # Entry point: Launches the GUI and initializes modules
# ├── gui/                            # GUI Module
# │   ├── __init__.py                 # Makes 'gui' a package
# │   ├── main_window.py              # Builds the main Tkinter window
# │   ├── video_display.py            # Handles video display in Tkinter canvas
# │   └── status_bar.py               # Handles the status bar for connection updates
# │
# ├── media/                          # Media Module (handles video/audio capture)
# │   ├── __init__.py                 # Makes 'media' a package
# │   ├── video_capture.py            # Video capture using OpenCV
# │   ├── audio_capture.py            # Audio capture using PyAudio
# │   └── media_streamer.py           # Combines video and audio capture into streams
# │
# ├── networking/                     # Networking Module
# │   ├── __init__.py                 # Makes 'networking' a package
# │   ├── signaling.py                # Handles signaling for WebRTC (e.g., peer setup)
# │   ├── p2p_connection.py           # Establishes and manages P2P communication
# │   └── data_transmitter.py         # Sends and receives video/audio data
# │
# ├── utils/                          # Utility functions (helpers)
# │   ├── __init__.py                 # Makes 'utils' a package
# │   ├── threading_utils.py          # Helpers for threading and concurrency
# │   ├── error_handler.py            # Error handling and logging
# │   └── config.py                   # Configuration settings (e.g., frame rate, resolution)
# │
# ├── assets/                         # Static assets (if needed)
# │   └── icons/                      # Icons/images for buttons or the app
# │
# └── README.md                       # Project documentation

Design document
https://docs.google.com/document/d/1jv3HUxBtLAEXc5tjUsdvlD8n1zvVc8xuDiwVRjxD2Do/edit?tab=t.0ing