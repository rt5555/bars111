import cv2
import numpy as np


class OverlayManager:
    def __init__(self):
        self.text = ""
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.position = (10, 30)
        self.scale = 0.8
        self.color = (255, 255, 255)
        self.thickness = 2
        self.logo = None
        self.logo_position = (10, 10)
        self.logo_alpha = 1.0

    def apply_overlays(self, frame):
        if self.text:
            frame = self.apply_text(frame)

        if self.logo is not None and self.logo_alpha > 0:
            frame = self.apply_logo(frame)

        return frame

    def apply_text(self, frame):
        cv2.putText(frame, self.text, self.position,
                    self.font, self.scale,
                    self.color, self.thickness)
        return frame

    def apply_logo(self, frame):
        logo_resized = cv2.resize(self.logo, (100, 100))
        alpha = self.logo_alpha

        y1, y2 = self.logo_position[1], self.logo_position[1] + logo_resized.shape[0]
        x1, x2 = self.logo_position[0], self.logo_position[0] + logo_resized.shape[1]

        if y2 > frame.shape[0] or x2 > frame.shape[1]:
            return frame

        roi = frame[y1:y2, x1:x2]
        blended = cv2.addWeighted(logo_resized, alpha, roi, 1 - alpha, 0)
        frame[y1:y2, x1:x2] = blended

        return frame
