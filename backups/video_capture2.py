import cv2
from PIL import Image, ImageTk


class VideoCapture:
    def __init__(self, dimensions=None, camera_index=0):
        """
        Initializes video capture from the default camera or specified camera index.
        """
        if dimensions is None:
            dimensions = {'width': 320, 'height': 240}

        self.camera_index = camera_index
        self.local_video_width = dimensions['width']
        self.local_video_height = dimensions['height']
        self.capture = cv2.VideoCapture(self.camera_index)
        self.running = False

    def get_frame(self):
        """
        Captures a single frame from the video feed, converts it to a format usable by Tkinter.
        Returns: A Tkinter-compatible image (PIL ImageTk.PhotoImage).
        """
        if not self.capture.isOpened():
            raise RuntimeError("Unable to open the video capture device.")

        ret, frame = self.capture.read()
        if not ret:
            return None

        # Resize the frame to fit the label size dynamically
        frame_resized = cv2.resize(frame, (self.local_video_width, self.local_video_height))

        # Convert the frame to RGB format for Tkinter
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))

        # Convert to Tkinter-compatible format
        return img

    def start(self):
        """
        Starts the video capture.
        """
        self.running = True

    def stop(self):
        """
        Stops the video capture and releases the camera.
        """
        self.running = False
        self.capture.release()
