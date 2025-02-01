import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk  # For rendering video frames in Tkinter

from gui.status_bar import StatusBar
import utils.error_handler as error_handler
import utils.config as config


class MainWindow:
    """
    Main GUI Window for the Linq'd livestream application.
    Handles user interactions and delegates media and networking logic.
    """

    def __init__(self,
                 root,
                 start_stream_callback,
                 stop_stream_callback,
                 get_local_frame_callback):
        """
        Initializes the GUI.

        Args:
            root: The Tkinter root window.
            start_stream_callback: Function to start the stream.
            stop_stream_callback: Function to stop the stream.
        """
        self.root = root
        self.root.title("Two-Person Live Streaming App")
        self.status_bar = StatusBar(self.root)
        self.start_stream_callback = start_stream_callback
        self.stop_stream_callback = stop_stream_callback
        self.get_local_frame_callback = get_local_frame_callback
        self.local_video_width = config.VIDEO_WIDTH
        self.local_video_height = config.VIDEO_HEIGHT
        self.local_video = None
        self.local_audio = None

        # UI Components
        self._create_widgets()

    def _create_widgets(self):
        # Title Label
        title_label = ttk.Label(self.root, text="Linq'd Live Stream", font=("Arial", 20, "bold"))
        title_label.pack(pady=10)

        # Connection Settings Frame
        connection_frame = ttk.Frame(self.root, padding=10)
        connection_frame.pack(pady=10)

        ttk.Label(connection_frame, text="Remote User ID:").grid(row=0, column=0, sticky="w")
        self.remote_user_entry = ttk.Entry(connection_frame, width=30)
        self.remote_user_entry.grid(row=0, column=1, padx=5)

        # connect_button = ttk.Button(connection_frame, text="Connect", command=self._on_connect)
        # connect_button.grid(row=0, column=2, padx=5)
        
        # disconnect_button = ttk.Button(connection_frame, text="Disconnect", command=self._on_disconnect)
        # disconnect_button.grid(row=0, column=3, padx=5)

        # Video Display Frames
        video_frame = ttk.Frame(self.root, padding=10)
        video_frame.pack(pady=10, expand=True, fill="both")

        # Local Video Display
        self.local_video_canvas = tk.Canvas(video_frame, bg="black", width=320, height=240)
        self.local_video_canvas.grid(row=0, column=0, pady=5)
        ttk.Label(video_frame, text="Local Video").grid(row=1, column=0, padx=10)

        # Remote Video Display
        self.remote_video_canvas = tk.Canvas(video_frame, bg="black", width=320, height=240)
        self.remote_video_canvas.grid(row=0, column=1, pady=5)
        ttk.Label(video_frame, text="Remote Video").grid(row=1, column=1, padx=10)

        # Control Buttons
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack()

        start_button = ttk.Button(control_frame, text="Start Stream", command=self.start_stream)
        start_button.grid(row=0, column=0, padx=10)

        stop_button = ttk.Button(control_frame, text="Stop Stream", command=self.stop_stream)
        stop_button.grid(row=0, column=1, padx=10)

    def start_stream(self):
        """
        Calls the start stream callback and updates the status.
        """
        try:
            self.status_bar.update_status("Initializing streams...")
            self.start_stream_callback()
            self.status_bar.update_status("Streaming started.")
            self._update_local_video()
        except Exception as e:
            error_handler.handle_exception(e, context="start_stream")
            self.status_bar.update_status("Error starting the stream.")

    def stop_stream(self):
        """
        Calls the stop stream callback and updates the status.
        """
        try:
            self.stop_stream_callback()
            self.status_bar.update_status("Streaming stopped.")
        except Exception as e:
            error_handler.handle_exception(e, context="stop_stream")
            self.status_bar.update_status("Error stopping the stream.")

    def _on_stop_stream(self):
        """
        Calls the stop stream callback and updates the status.
        """
        try:
            self.stop_stream_callback()
            self.status_bar.update_status("Streaming stopped.")
        except Exception as e:
            error_handler.handle_exception(e, context="stop_stream")
            self.status_bar.update_status("Error stopping the stream.")

    def _update_local_video(self):
        """
        Continuously updates the video canvas with the local video frame.
        """
        try:
            frame = self.get_local_frame_callback()
            if frame is not None:
                # Convert frame (numpy array) to a format compatible with Tkinter
                image = Image.fromarray(frame)

                # Resize the frame to fit the label size dynamically
                frame_resized = image.resize((self.local_video_width, self.local_video_height))
                
                photo = ImageTk.PhotoImage(image=frame_resized)
                self.local_video_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
                self.local_video_canvas.image = photo  # Keep a reference to prevent garbage collection

        except Exception as e:
            error_handler.handle_exception(e, context="MainWindow._update_local_video")

        # Schedule the next frame update
        self.root.after(33, self._update_local_video)  # ~30 FPS

    def on_close(self):
        self._on_stop_stream()
        self.root.destroy()

