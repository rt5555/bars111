import cv2
import time
from onvif import ONVIFCamera

class CameraConnector:
    def __init__(self):
        self.cap = None
        self.retry_interval = 5  # секунды между попытками

    def connect_via_onvif(self, ip, login, password):
        """Подключение к камере через ONVIF (для ГРОК и других)"""
        try:
            cam = ONVIFCamera(ip, 80, login, password)
            media = cam.create_media_service()
            profiles = media.GetProfiles()
            stream_uri = media.GetStreamUri({
                'StreamSetup': {'Stream': 'RTP-Unicast', 'Transport': 'RTSP'},
                'ProfileToken': profiles[0].token
            })
            return stream_uri.Uri
        except Exception as e:
            print(f"ONVIF Error: {e}")
            return None

    def stable_capture(self, rtsp_url, max_retries=5):
        """Захват видео с автопереподключением"""
        retry_count = 0
        while retry_count < max_retries:
            try:
                self.cap = cv2.VideoCapture(rtsp_url)
                while self.cap.isOpened():
                    ret, frame = self.cap.read()
                    if not ret:
                        break
                    yield frame
                self.cap.release()
            except:
                retry_count += 1
                time.sleep(self.retry_interval)
        raise ConnectionError(f"Не удалось подключиться после {max_retries} попыток")

    def disconnect(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()