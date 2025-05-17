from plugin_interface import CameraPlugin
import requests


class GrokCameraPlugin(CameraPlugin):
    def get_supported_models(self):
        return ['GROK-X1', 'GROK-X2 Pro']

    def connect(self, ip, credentials):
        try:
            response = requests.get(f"http://{ip}/api/connect",
                                    auth=(credentials['user'], credentials['password']))
            return response.status_code == 200
        except:
            return False

    def get_camera_parameters(self):
        return {
            'resolution': ['1080p', '2K', '4K'],
            'fps': [30, 60],
            'special_modes': ['night_vision', 'thermal']
        }