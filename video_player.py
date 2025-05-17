from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSlider
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl
from PyQt6.QtCore import Qt  # Добавьте в начало файла

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.video_widget = QVideoWidget()
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()

        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.video_widget)

        self.play_btn = QPushButton("Воспроизвести")
        self.play_btn.clicked.connect(self.toggle_play)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.sliderMoved.connect(self.set_position)

        layout.addWidget(self.video_widget)
        layout.addWidget(self.play_btn)
        layout.addWidget(self.slider)
        self.setLayout(layout)

    def load_video(self, path):
        self.player.setSource(QUrl.fromLocalFile(path))

    def toggle_play(self):
        if self.player.isPlaying():
            self.player.pause()
            self.play_btn.setText("Воспроизвести")
        else:
            self.player.play()
            self.play_btn.setText("Пауза")

    def set_position(self, position):
        self.player.setPosition(position)