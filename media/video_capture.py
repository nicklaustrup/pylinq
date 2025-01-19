import asyncio
import cv2
import threading
from aiortc.mediastreams import VideoStreamTrack
from av import VideoFrame

import utils.threading_utils as thread_utils
import utils.config as config
import utils.error_handler as error_handler


class VideoCapture(VideoStreamTrack):
    """
    Captures video frames using OpenCV and provides them as a WebRTC-compatible track.
    """

    def __init__(self, source=config.VIDEO_SOURCE):
        """
        Initializes the video capture settings.

        Args:
            source (int or str): Video source (default is 0 for webcam).
        """
        super().__init__()  # Initialize VideoStreamTrack
        self.source = source
        self.capture = cv2.VideoCapture(self.source)
        self.running = False
        self.thread = None
        self.frame = None  # Holds the latest video frame
        self.lock = threading.Lock()

    def start(self) -> None:
        """
        Starts the video capture stream and frame retrieval thread.
        """
        try:
            if self.running:
                error_handler.log_info("Video capture is already running.")
                return

            error_handler.log_info("Starting video capture...")
            self.running = True
            self.thread = thread_utils.run_in_background(self._capture_frames)
        except Exception as e:
            error_handler.handle_exception(e, context="VideoCapture.start")

    def get_frame(self):
        """
        Retrieves the latest video frame as a numpy array.

        Returns:
            numpy.ndarray: The most recent video frame, or None if no frame is available.
        """
        with self.lock:
            if self.frame is not None:
                copy = self.frame.copy()
                # Convert frame (numpy array) from BGR to RGB
                frame_rgb = cv2.cvtColor(copy, cv2.COLOR_BGR2RGB)
                return frame_rgb
            else:
                return None

    def _capture_frames(self) -> None:
        """
        Continuously captures video frames and stores the latest one.
        """
        try:
            if not self.capture.isOpened():
                error_handler.log_error("Failed to open video capture source.")
                self.running = False
                return

            while self.running:
                ret, frame = self.capture.read()
                if not ret:
                    error_handler.log_warning("Failed to capture video frame.")
                    continue
                with self.lock:
                    self.frame = frame
        except Exception as e:
            error_handler.handle_exception(e, context="VideoCapture._capture_frames")

    async def recv(self) -> VideoFrame:
        """
        Provides video frames to WebRTC (required by aiortc).

        Returns:
            VideoFrame: The next video frame.
        """
        try:
            pts, time_base = await self.next_timestamp()
            with self.lock:
                if self.frame is not None:
                    # Convert the frame to VideoFrame (required for WebRTC)
                    video_frame = VideoFrame.from_ndarray(self.frame, format="bgr24")
                    video_frame.pts = pts
                    video_frame.time_base = time_base
                    return video_frame
            await asyncio.sleep(0)  # Yield control to avoid blocking
        except Exception as e:
            error_handler.handle_exception(e, context="VideoCapture.recv")

    def stop(self) -> None:
        """
        Stops the video capture and releases the camera.
        """
        try:
            if not self.running:
                error_handler.log_error("Video capture is not running.")
                return

            error_handler.log_info("Stopping video capture...")
            self.running = False
            thread_utils.stop_thread(self.thread)
            self.capture.release()
            error_handler.log_info("Video capture stopped.")
        except Exception as e:
            error_handler.handle_exception(e, context="VideoCapture.stop")