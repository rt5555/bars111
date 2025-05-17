from pymavlink import mavutil

class TelemetryReader:
    def __init__(self, port='udp:127.0.0.1:14550'):
        self.connection = mavutil.mavlink_connection(port)

    def get_battery_status(self):
        """Чтение данных о батарее"""
        msg = self.connection.recv_match(type='BATTERY_STATUS', blocking=True, timeout=5)
        if msg:
            return {
                'percentage': msg.battery_remaining,
                'voltage': msg.voltages[0] / 1000  # Вольты
            }
        return None

    def get_signal_strength(self):
        """Уровень сигнала RX/TX"""
        msg = self.connection.recv_match(type='RADIO_STATUS', blocking=True, timeout=5)
        if msg:
            return {
                'rx': msg.rssi,
                'tx': msg.remrssi
            }
        return None