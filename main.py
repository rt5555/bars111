import sys
import os

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QComboBox, QLineEdit, QTextEdit, QSlider,
                             QFileDialog, QMessageBox, QStatusBar, QSizePolicy, QFrame,
                             QInputDialog)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QImage, QPixmap, QFont, QTextCursor
import datetime
import json

from mavlink_thread import CameraThread
from camera_settings import CameraSettingsDialog
from recording_manager import RecordingManager
from overlay_engine import OverlayManager
from telemetry import TelemetryReader
from camera_discovery import CameraDiscovery


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Видеоаналитика IP-камер")
        self.setGeometry(100, 100, 1000, 700)

        # Инициализация компонентов
        self.recording_manager = RecordingManager()
        self.overlay_manager = OverlayManager()
        self.telemetry_parser = TelemetryReader()
        self.network_scanner = CameraDiscovery()

        self.init_ui()
        self.init_connections()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Верхняя панель (видео + телеметрия)
        top_panel = QHBoxLayout()
        main_layout.addLayout(top_panel, stretch=4)

        # Видео панель
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("background-color: black;")
        top_panel.addWidget(self.video_label, stretch=3)

        # Панель телеметрии
        telemetry_panel = QVBoxLayout()
        telemetry_panel.setSpacing(10)
        top_panel.addLayout(telemetry_panel, stretch=1)

        # Элементы телеметрии
        self.telemetry_labels = {
            'battery': QLabel("Заряд: --%"),
            'voltage': QLabel("Напряжение: -- В"),
            'signal': QLabel("Сигнал: --%"),
            'fps': QLabel("FPS: --"),
            'status': QLabel("Статус: Нет данных")
        }

        for label in self.telemetry_labels.values():
            label.setStyleSheet("font-size: 14px;")
            telemetry_panel.addWidget(label)

        telemetry_panel.addStretch()

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Индикатор соединения
        self.connection_indicator = QLabel()
        self.connection_indicator.setFixedSize(20, 20)
        self.update_connection_status("disconnected")
        telemetry_panel.addWidget(self.connection_indicator, alignment=Qt.AlignmentFlag.AlignRight)

        # Панель управления
        control_panel = QHBoxLayout()
        main_layout.addLayout(control_panel)

        # Кнопки управления
        self.control_buttons = {
            'connect': QPushButton("Подключиться"),
            'settings': QPushButton("Настройки"),
            'record': QPushButton("Запись"),
            'screenshot': QPushButton("Снимок"),
            'fullscreen': QPushButton("Полный экран"),
            'scan': QPushButton("Поиск камер")
        }

        for btn in self.control_buttons.values():
            control_panel.addWidget(btn)

        self.control_buttons['record'].setEnabled(False)
        self.control_buttons['screenshot'].setEnabled(False)

        # Панель логов
        self.log_panel = QTextEdit()
        self.log_panel.setReadOnly(True)
        self.log_panel.setMaximumHeight(100)
        self.log_panel.setStyleSheet("font-family: Consolas; font-size: 10px;")
        main_layout.addWidget(self.log_panel)

        # Поток камеры
        self.camera_thread = None

    def init_connections(self):
        self.control_buttons['connect'].clicked.connect(self.toggle_connection)
        self.control_buttons['settings'].clicked.connect(self.show_settings)
        self.control_buttons['record'].clicked.connect(self.toggle_recording)
        self.control_buttons['screenshot'].clicked.connect(self.take_screenshot)
        self.control_buttons['fullscreen'].clicked.connect(self.toggle_fullscreen)
        self.control_buttons['scan'].clicked.connect(self.scan_network)

    def toggle_connection(self):
        if self.camera_thread and self.camera_thread.isRunning():
            self.disconnect_camera()
        else:
            self.connect_camera()

    def connect_camera(self):
        try:
            sources = [
                ("Локальная камера (0)", "0"),
                ("Локальная камера (1)", "1"),
                ("Тестовое видео", "test_video"),
                ("Ввести вручную", "manual")
            ]

            source_name, ok = QInputDialog.getItem(
                self, "Выбор камеры", "Выберите источник:",
                [s[0] for s in sources], 0, False
            )
            if not ok:
                return

            source = next((s[1] for s in sources if s[0] == source_name), "0")

            if source == "manual":
                source, ok = QInputDialog.getText(
                    self, "Ручной ввод",
                    "Введите URL/IP/номер камеры или путь к видео:\n(Пример: C:/видео.mp4)",
                    QLineEdit.EchoMode.Normal, ""
                )
                if not ok:
                    return

                # Проверка существования файла
                if not source.isdigit() and not source.startswith(('rtsp://', 'http://')):
                    if not os.path.exists(source):
                        self.log_error(f"Файл не найден: {source}")
                        return

            elif source == "test_video":
                # Создаем тестовое видео если его нет
                if not os.path.exists("test_video.mp4"):
                    self.create_test_video()
                source = "test_video.mp4"

            self.log_message(f"Подключение к: {source}")

            # Останавливаем предыдущее подключение если было
            if hasattr(self, 'camera_thread') and self.camera_thread:
                self.disconnect_camera()

            # Создаем новый поток
            self.camera_thread = CameraThread(source)
            self.camera_thread.change_pixmap.connect(self.update_image)
            self.camera_thread.error_occurred.connect(self.handle_camera_error)
            self.camera_thread.start()

            self.control_buttons['connect'].setText("Отключиться")
            self.control_buttons['record'].setEnabled(True)
            self.control_buttons['screenshot'].setEnabled(True)

        except Exception as e:
            self.log_error(f"Ошибка подключения: {str(e)}")
            import traceback
            traceback.print_exc()

    def handle_camera_error(self, message):
        self.log_error(message)
        self.disconnect_camera()  # Безопасное отключение

    def disconnect_camera(self):
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread.wait()
            self.camera_thread = None

            self.video_label.clear()
            self.video_label.setStyleSheet("background-color: black;")

            self.control_buttons['connect'].setText("Подключиться")
            self.control_buttons['record'].setEnabled(False)
            self.control_buttons['screenshot'].setEnabled(False)
            self.control_buttons['record'].setText("Запись")

            self.update_connection_status("disconnected")
            self.log_message("Камера отключена")

    def show_settings(self):
        if not self.camera_thread or not self.camera_thread.isRunning():
            QMessageBox.warning(self, "Ошибка", "Сначала подключитесь к камере")
            return

        settings_dialog = CameraSettingsDialog(self.camera_thread, self)
        settings_dialog.exec_()

    def toggle_recording(self):
        if not self.recording_manager.is_recording():
            filename = self.prepare_recording_filename()
            if filename:
                try:
                    self.camera_thread.start_recording(filename)
                    self.recording_manager.start_recording(filename)
                    self.control_buttons['record'].setText("Стоп")
                    self.log_message(f"Начата запись: {filename}")
                except Exception as e:
                    self.log_error(f"Ошибка начала записи: {str(e)}")
        else:
            self.camera_thread.stop_recording()
            duration = self.recording_manager.stop_recording()
            self.control_buttons['record'].setText("Запись")
            self.log_message(f"Запись остановлена. Длительность: {duration:.1f} сек")

    def prepare_recording_filename(self):
        default_dir = self.config.get('recordings_dir', os.path.expanduser("~/Videos"))
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"recording_{timestamp}.mp4"

        if not os.path.exists(default_dir):
            os.makedirs(default_dir)

        return os.path.join(default_dir, default_name)

    def take_screenshot(self):
        if self.camera_thread:
            default_dir = self.config.get('screenshots_dir', os.path.expanduser("~/Pictures"))
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"screenshot_{timestamp}.jpg"

            if not os.path.exists(default_dir):
                os.makedirs(default_dir)

            filename = os.path.join(default_dir, default_name)
            if self.camera_thread.take_screenshot(filename):
                self.log_message(f"Снимок сохранен: {filename}")
            else:
                self.log_error("Не удалось сохранить снимок")

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.control_buttons['fullscreen'].setText("Полный экран")
        else:
            self.showFullScreen()
            self.control_buttons['fullscreen'].setText("Оконный режим")

    def scan_network(self):
        self.log_message("Поиск камер в сети...")
        QApplication.processEvents()  # Обновляем GUI

        try:
            found_cameras = self.network_scanner.scan()
            if not found_cameras:  # Если список пуст
                self.log_message("Камеры не найдены")
                return

            self.log_message(f"Найдено камер: {len(found_cameras)}")
            for cam in found_cameras:
                self.log_message(f" - {cam.get('name', 'Без имени')} ({cam.get('address', 'N/A')})")

        except Exception as e:
            self.log_error(f"Ошибка сканирования: {str(e)}")

    def update_image(self, image):
        self.video_label.setPixmap(QPixmap.fromImage(image))

    def update_connection_status(self, status):
        color_map = {
            "connected": "green",
            "disconnected": "red",
            "unstable": "yellow"
        }

        if status in color_map:
            self.connection_indicator.setStyleSheet(
                f"background-color: {color_map[status]}; border-radius: 10px;")

            status_texts = {
                "connected": "Камера подключена",
                "unstable": "Нестабильное соединение",
                "disconnected": "Камера отключена"
            }
            self.status_bar.showMessage(status_texts.get(status, ""))

    def update_telemetry(self, data):
        self.telemetry_labels['battery'].setText(f"Заряд: {data.get('battery_level', '--')}%")
        self.telemetry_labels['voltage'].setText(f"Напряжение: {data.get('voltage', '--')} В")
        self.telemetry_labels['signal'].setText(f"Сигнал: {data.get('signal_strength', '--')}%")
        self.telemetry_labels['fps'].setText(f"FPS: {data.get('fps', '--')}")
        self.telemetry_labels['status'].setText(f"Статус: {data.get('status', 'Нет данных')}")

        # Обновить индикатор соединения
        signal = data.get('signal_strength', 0)
        if signal > 70:
            self.update_connection_status("connected")
        elif signal > 30:
            self.update_connection_status("unstable")
        else:
            self.update_connection_status("disconnected")

    def log_message(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_panel.append(f"[{timestamp}] {message}")
        self.log_panel.moveCursor(QTextCursor.MoveOperation.End)

    def log_error(self, error):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_panel.append(f"[{timestamp}] ОШИБКА: {error}")
        self.log_panel.moveCursor(QTextCursor.MoveOperation.End)  # Изменено для PyQt6
        self.status_bar.showMessage(error)

    def closeEvent(self, event):
        self.disconnect_camera()
        self.config.save()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
