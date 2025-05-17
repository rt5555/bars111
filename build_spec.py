# build.spec
from PyInstaller.building.api import EXE
from PyInstaller.building.build_main import Analysis

block_cipher = None

a = Analysis(
    ['main.py'],  # Главный файл вашего приложения
    pathex=[],     # Пути к дополнительным файлам (если есть)
    binaries=[],
    datas=[],      # Сюда добавьте пути к логотипам, шрифтам и т.д.
    hiddenimports=['cv2', 'PyQt5'],  # Скрытые зависимости
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
exe = EXE(
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='IPCameraApp',  # Имя вашего .exe
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,           # Сжатие (уменьшит размер .exe)
    console=False,      # Запуск без консоли (только GUI)
    onefile=True,       # Собрать в ОДИН .exe
)