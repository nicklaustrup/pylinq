import tkinter as tk
from tkinter import ttk

from gui.status_bar import StatusBar
import utils.error_handler as error_handler


class MainWindow:
    """
    Main GUI Window for the Linq'd livestream application.
    Handles user interactions and delegates media and networking logic.
    """

    def __init__(self, root, start_stream_callback, stop_stream_callback):
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
        self.local_video = None
        self.local_audio = None

        # UI Components
        self._create_widgets()
        # self.start_button = tk.Button(root, text="Start Stream", command=self.start_stream)
        # self.start_button.pack(pady=10)
        #
        # self.stop_button = tk.Button(root, text="Stop Stream", command=self.stop_stream)
        # self.stop_button.pack(pady=10)

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

        connect_button = ttk.Button(connection_frame, text="Connect", command=self._on_connect)
        connect_button.grid(row=0, column=2, padx=5)

        disconnect_button = ttk.Button(connection_frame, text="Disconnect", command=self._on_disconnect)
        disconnect_button.grid(row=0, column=3, padx=5)

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

        # # Status Bar
        # self.status_label = ttk.Label(self.root, text="Status: Ready", anchor="w", relief="sunken")
        # self.status_label.pack(side="bottom", fill="x")

    def start_stream(self):
        """
        Calls the start stream callback and updates the status.
        """
        try:
            self.status_bar.update_status("Initializing streams...")
            # self._update_local_video()
            self.start_stream_callback()
            self.local_video = None
            self.local_audio = None
            self.status_bar.update_status("Streaming started.")
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

    # # Placeholder methods for button commands
    def _on_connect(self):
        self.status_bar.update_status(text="Status: Connecting...")
        error_handler.log_info(f"Connecting to remote user: {self.remote_user_entry.get()}")

    def _on_disconnect(self):
        self.status_bar.update_status(text="Status: Disconnected")
        error_handler.log_info("Disconnected from remote user.")
        self.running = False
        self.stop_stream_callback()

    #
    # def _on_start_stream(self):
    #     self.status_label.config(text="Status: Streaming started...")
    #     self.running = True
    #     self.video_capture.start()
    #     self._update_local_video()
    #
    def _on_stop_stream(self):
        self.status_bar.update_status(text="Status: Streaming stopped")
        self.running = False
        self.stop_stream_callback()

    def _update_local_video(self):
        if self.running:
            frame = self.local_video.get_frame()
            if frame:
                # Update the label with the new image
                self.local_video_canvas.imgtk = frame
                # self.local_video_canvas.configure(image=frame)

                self.local_video_canvas.create_image(0, 0, anchor=tk.NW, image=frame)
                self.local_video_canvas.image = frame  # Keep a reference to prevent garbage collection
            self.after(10, self._update_local_video)  # Schedule the next frame update

    def on_close(self):
        self._on_stop_stream()
        self.root.destroy()

