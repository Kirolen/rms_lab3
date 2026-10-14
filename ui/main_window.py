from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from ui.image_panel import ImagePanel


WINDOW_STYLE = """
QMainWindow, QWidget { background-color: #171c26; color: #e6edf7; }
QLabel#heading { font-size: 24px; font-weight: 600; }
QLabel#subtitle { color: #a4b1c5; font-size: 13px; }
QFrame#imagePanel {
    background-color: #222b3a;
    border: 1px solid #364359;
    border-radius: 10px;
}
QLabel#panelTitle { background: transparent; font-size: 18px; font-weight: 600; }
QLabel#imagePreview {
    background-color: #111722;
    color: #8e9db4;
    border: 1px dashed #3d4c63;
    border-radius: 6px;
    padding: 16px;
}
QStatusBar { color: #a4b1c5; }
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Стиснення зображень — DCT / DWT")
        self.resize(1100, 650)
        self.setMinimumSize(760, 480)
        self.setStyleSheet(WINDOW_STYLE)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(24, 24, 24, 16)
        layout.setSpacing(16)

        heading = QLabel("Порівняння стиснення зображень")
        heading.setObjectName("heading")
        subtitle = QLabel("Оригінальне зображення та результати DCT і DWT")
        subtitle.setObjectName("subtitle")
        layout.addWidget(heading)
        layout.addWidget(subtitle)

        self.original_panel = ImagePanel("Original", "Зображення не завантажено")
        self.dct_panel = ImagePanel("DCT", "Результат косинусного перетворення")
        self.dwt_panel = ImagePanel("DWT", "Результат вейвлет-перетворення Хаара")

        panels_layout = QHBoxLayout()
        panels_layout.setSpacing(16)
        for panel in (self.original_panel, self.dct_panel, self.dwt_panel):
            panels_layout.addWidget(panel, stretch=1)
        layout.addLayout(panels_layout, stretch=1)
        self.statusBar().showMessage("Готово")
