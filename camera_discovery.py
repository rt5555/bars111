from PyQt6.QtCore import QThread, pyqtSignal

class CameraScanner(QThread):
    finished = pyqtSignal(list)  # Список найденных камер

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            cameras = self.scan_network()  # Твой метод сканирования
            self.finished.emit(cameras)
        except Exception as e:
            self.finished.emit([])

class CameraDiscovery:
    def __init__(self):
        self.scanner = CameraScanner()
        self.scanner.finished.connect(self.on_scan_finished)

    def scan(self):
        self.scanner.start()  # Запуск в отдельном потоке

    def on_scan_finished(self, cameras):
        return cameras  # Или обновляй GUI здесь