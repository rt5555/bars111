from pymavlink import mavutil
import serial.tools.list_ports


class MAVLinkReader:
    def __init__(self, port=None):
        self.connection = None
        self.port = self._detect_port() if port is None else port

        if self.port:
            try:
                self.connection = mavutil.mavlink_connection(self.port)
                print(f"Connected to MAVLink device on {self.port}")
            except Exception as e:
                print(f"MAVLink connection failed: {e}")

    def _detect_port(self):
        """Автопоиск подходящего COM-порта"""
        mavlink_ports = []
        ports = serial.tools.list_ports.comports()

        for port in ports:
            if 'USB' in port.description or 'Serial' in port.description:
                mavlink_ports.append(port.device)

        return mavlink_ports[0] if mavlink_ports else None

    def scan_ports(self):
        ports = serial.tools.list_ports.comports()
        if not ports:
            self.status_label.setText("No COM ports found")
        else:
            self.status_label.setText(f"Available ports: {[p.device for p in ports]}")

    def get_telemetry(self):
        if not self.connection:
            return {'error': 'No MAVLink connection'}

        try:
            msg = self.connection.recv_match(type='SYS_STATUS', blocking=True, timeout=2)
            if msg:
                return {
                    'battery': msg.battery_remaining,
                    'voltage': msg.voltage_battery / 1000,
                    'rssi': msg.communication_rssi
                }
            return {'warning': 'No telemetry data'}
        except Exception as e:
            return {'error': str(e)}