import time
import os


class RecordingManager:
    def __init__(self):
        self._recording = False
        self.start_time = 0
        self.filename = ""

    def start_recording(self, filename):
        self._recording = True
        self.start_time = time.time()
        self.filename = filename

        # Создаем папку если нужно
        os.makedirs(os.path.dirname(filename), exist_ok=True)

    def stop_recording(self):
        self._recording = False
        duration = time.time() - self.start_time
        self.start_time = 0
        return duration

    def is_recording(self):
        return self._recording

    def get_current_filename(self):
        return self.filename if self._recording else ""
