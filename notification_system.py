from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer


class NotificationSystem:
    def __init__(self, parent):
        self.parent = parent
        self.tray = QSystemTrayIcon(QIcon("icon.png"), parent)
        self.setup_tray()

    def setup_tray(self):
        menu = QMenu()
        restore_action = menu.addAction("Открыть")
        exit_action = menu.addAction("Выход")
        restore_action.triggered.connect(self.parent.showNormal)
        exit_action.triggered.connect(self.parent.close)
        self.tray.setContextMenu(menu)
        self.tray.show()

    def show_notification(self, title, message):
        self.tray.showMessage(title, message, QSystemTrayIcon.Information, 3000)