import json
import os
from dataclasses import dataclass


@dataclass
class CameraProfile:
    name: str
    ip: str
    port: int
    rtsp_path: str
    brightness: float = 0.5
    contrast: float = 0.5
    resolution: tuple = (1920, 1080)


class CameraProfileManager:
    def __init__(self):
        self.profiles = self.load_profiles()
        self.current_profile = None

    def load_profiles(self):
        if not os.path.exists('camera_profiles.json'):
            return {}

        with open('camera_profiles.json') as f:
            data = json.load(f)
            return {name: CameraProfile(**params) for name, params in data.items()}

    def save_profiles(self):
        with open('camera_profiles.json', 'w') as f:
            json.dump({name: vars(profile) for name, profile in self.profiles.items()}, f)

    def create_profile(self, name, ip, port, rtsp_path):
        self.profiles[name] = CameraProfile(name, ip, port, rtsp_path)
        self.save_profiles()

    def delete_profile(self, name):
        if name in self.profiles:
            del self.profiles[name]
            self.save_profiles()