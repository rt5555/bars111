import cv2
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QSlider, QLineEdit, QPushButton, QFileDialog,
                             QMessageBox)
from PyQt6.QtCore import Qt


class CameraSettingsDialog(QWidget):
    def __init__(self, camera_thread, parent=None):
        super().__init__(parent)
        self.camera_thread = camera_thread
        self.setWindowTitle("Настройки камеры")
        self.setFixedSize(400, 400)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Настройки изображения
        self.brightness_slider = self.create_setting_slider("Яркость", 0, 100,
                                                            self.camera_thread.camera_settings['brightness'],
                                                            self.update_brightness)
        layout.addLayout(self.brightness_slider)

        self.contrast_slider = self.create_setting_slider("Контраст", 0, 100,
                                                          self.camera_thread.camera_settings['contrast'],
                                                          self.update_contrast)
        layout.addLayout(self.contrast_slider)

        self.saturation_slider = self.create_setting_slider("Насыщенность", 0, 100,
                                                            self.camera_thread.camera_settings['saturation'],
                                                            self.update_saturation)
        layout.addLayout(self.saturation_slider)

        self.exposure_slider = self.create_setting_slider("Экспозиция", 0, 100,
                                                          self.camera_thread.camera_settings['exposure'],
                                                          self.update_exposure)
        layout.addLayout(self.exposure_slider)

        self.hue_slider = self.create_setting_slider("Оттенок", 0, 100,
                                                     self.camera_thread.camera_settings['hue'],
                                                     self.update_hue)
        layout.addLayout(self.hue_slider)

        # Наложение текста
        layout.addWidget(QLabel("Текст наложения:"))
        self.overlay_text_edit = QLineEdit(self.camera_thread.overlay_text)
        self.overlay_text_edit.textChanged.connect(self.update_overlay_text)
        layout.addWidget(self.overlay_text_edit)

        # Кнопка загрузки лого
        self.load_logo_btn = QPushButton("Загрузить логотип")
        self.load_logo_btn.clicked.connect(self.load_logo)
        layout.addWidget(self.load_logo_btn)

        # Прозрачность лого
        self.logo_alpha_slider = self.create_setting_slider("Прозрачность лого", 0, 100,
                                                            int(self.camera_thread.logo_alpha * 100),
                                                            self.update_logo_alpha)
        layout.addLayout(self.logo_alpha_slider)

        self.setLayout(layout)

    def create_setting_slider(self, label, min_val, max_val, init_val, callback):
        layout = QHBoxLayout()

        name_label = QLabel(label)
        layout.addWidget(name_label)

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(init_val)
        slider.valueChanged.connect(callback)
        layout.addWidget(slider)

        value_label = QLabel(str(init_val))
        slider.valueChanged.connect(lambda v: value_label.setText(str(v)))
        layout.addWidget(value_label)

        return layout

    def update_brightness(self, value):
        self.camera_thread.set_camera_property('brightness', value)

    def update_contrast(self, value):
        self.camera_thread.set_camera_property('contrast', value)

    def update_saturation(self, value):
        self.camera_thread.set_camera_property('saturation', value)

    def update_exposure(self, value):
        self.camera_thread.set_camera_property('exposure', value)

    def update_hue(self, value):
        self.camera_thread.set_camera_property('hue', value)

    def update_overlay_text(self, text):
        self.camera_thread.overlay_text = text

    def load_logo(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Выберите логотип", "",
                                                  "Images (*.png *.jpg *.jpeg *.bmp)")
        if filename:
            try:
                self.camera_thread.logo = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
                if self.camera_thread.logo is None:
                    raise Exception("Не удалось загрузить изображение")

                # Конвертируем RGBA в RGB если нужно
                if self.camera_thread.logo.shape[2] == 4:
                    self.camera_thread.logo = cv2.cvtColor(self.camera_thread.logo, cv2.COLOR_RGBA2RGB)

                QMessageBox.information(self, "Успех", "Логотип успешно загружен")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить логотип: {str(e)}")

    def update_logo_alpha(self, value):
        self.camera_thread.logo_alpha = value / 100.0
