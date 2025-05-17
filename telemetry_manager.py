import serial
from PyQt6.QtCore import QObject, pyqtSignal
from pymavlink import mavutil
import json
import os


class TelemetryManager(QObject):
    telemetry_updated = pyqtSignal(dict)
    connection_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.connection = None
        self.active_profile = None
        self.profiles = self.load_profiles()

    def connect_to_fc(self, port=None):
        try:
            port = port or self.active_profile.get('port') if self.active_profile else None
            if not port:
                ports = [p.device for p in serial.tools.list_ports.comports()]
                port = ports[0] if ports else 'udpin:0.0.0.0:14550'

            self.connection = mavutil.mavlink_connection(port)
            self.connection_changed.emit(True)
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            self.connection_changed.emit(False)
            return False

    def update_telemetry(self):
        while self.connection:
            try:
                msg = self.connection.recv_match(type=['SYS_STATUS', 'GPS_RAW_INT'], blocking=True, timeout=2)
                if msg:
                    data = {
                        'battery': getattr(msg, 'battery_remaining', 0),
                        'voltage': getattr(msg, 'voltage_battery', 0) / 1000,
                        'lat': getattr(msg, 'lat', 0) / 1e7,
                        'lon': getattr(msg, 'lon', 0) / 1e7,
                        'alt': getattr(msg, 'alt', 0) / 1000
                    }
                    self.telemetry_updated.emit(data)
            except:
                self.connection_changed.emit(False)
                break

    def load_profiles(self):
        if not os.path.exists('telemetry_profiles.json'):
            return {}

        with open('telemetry_profiles.json') as f:
            return json.load(f)

    def save_profiles(self):
        with open('telemetry_profiles.json', 'w') as f:
            json.dump(self.profiles, f)