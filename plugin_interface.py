from abc import ABC, abstractmethod


class CameraPlugin(ABC):
    @abstractmethod
    def get_supported_models(self):
        pass

    @abstractmethod
    def connect(self, ip, credentials):
        pass

    @abstractmethod
    def get_camera_parameters(self):
        pass