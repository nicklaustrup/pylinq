import socket
import threading


class StreamManager:
    def __init__(self, local_ip, local_port, remote_ip, remote_port):
        self.local_ip = local_ip
        self.local_port = local_port
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.is_running = False

    def start(self, audio_callback):
        """Start receiving audio data."""
        self.is_running = True
        self.sock.bind((self.local_ip, self.local_port))
        threading.Thread(target=self._receive_loop, args=(audio_callback,), daemon=True).start()

    def _receive_loop(self, audio_callback):
        """Continuously receive audio data and pass it to the callback."""
        print("Receiving audio data...")
        while self.is_running:
            try:
                data, _ = self.sock.recvfrom(2048)  # Receive audio data chunks
                audio_callback(data)  # Send to callback for playback
            except Exception as e:
                print(f"Error receiving data: {e}")
                self.stop()

    def send_audio(self, data):
        """Send audio data to the remote peer."""
        try:
            self.sock.sendto(data, (self.remote_ip, self.remote_port))
        except Exception as e:
            print(f"Error sending data: {e}")

    def stop(self):
        """Stop the stream manager."""
        self.is_running = False
        self.sock.close()
        print("Stream manager stopped.")
