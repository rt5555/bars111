import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
import time

from PyQt6.QtGui import QImage


class CameraThread(QThread):
    change_pixmap = pyqtSignal(QImage)
    error_occurred = pyqtSignal(str)

    def __init__(self, source):
        super().__init__()
        self.source = source
        self._running = False

    def run(self):
        self._running = True
        cap = None
        try:
            # Определяем тип источника
            if isinstance(self.source, str) and self.source.isdigit():
                cap = cv2.VideoCapture(int(self.source))  # Камера
            else:
                cap = cv2.VideoCapture(self.source)  # Файл/URL

            if not cap.isOpened():
                raise RuntimeError("Не удалось открыть источник видео")

            while self._running:
                ret, frame = cap.read()
                if not ret:
                    raise RuntimeError("Ошибка чтения кадра")

                # Обработка кадра
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                self.change_pixmap.emit(qt_image)

                # Ограничение FPS
                self.msleep(30)

        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            if cap:
                cap.release()
            self._running = False

    def stop(self):
        self._running = False
        self.wait()