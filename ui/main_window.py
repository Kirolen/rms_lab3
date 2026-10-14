from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from pathlib import Path

from processing.image_io import load_grayscale_image
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
QPushButton {
    background-color: #366bd6; border: none; border-radius: 6px;
    padding: 10px 16px; font-size: 13px;
}
QPushButton:hover { background-color: #477de8; }
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.original_image = None
        self.image_path = None
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

        self.open_button = QPushButton("Відкрити зображення")
        self.open_button.clicked.connect(self._open_image)
        self.image_info = QLabel("Зображення не вибрано")
        self.image_info.setWordWrap(True)
        self.image_info.setObjectName("subtitle")
        toolbar = QHBoxLayout()
        toolbar.addWidget(self.open_button)
        toolbar.addWidget(self.image_info, stretch=1)
        layout.addLayout(toolbar)

        self.original_panel = ImagePanel("Original", "Зображення не завантажено")
        self.dct_panel = ImagePanel("DCT", "Результат косинусного перетворення")
        self.dwt_panel = ImagePanel("DWT", "Результат вейвлет-перетворення Хаара")

        panels_layout = QHBoxLayout()
        panels_layout.setSpacing(16)
        for panel in (self.original_panel, self.dct_panel, self.dwt_panel):
            panels_layout.addWidget(panel, stretch=1)
        layout.addLayout(panels_layout, stretch=1)
        self.statusBar().showMessage("Готово")

    def _open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Виберіть зображення", "",
            "Зображення (*.png *.jpg *.jpeg *.bmp *.webp);;Усі файли (*)",
        )
        if file_path:
            self.load_image(file_path)

    def load_image(self, file_path):
        try:
            image, original_size = load_grayscale_image(file_path)
        except ValueError as error:
            QMessageBox.warning(self, "Помилка відкриття", str(error))
            return False

        self.original_image = image
        self.image_path = str(file_path)
        self.original_panel.set_image(image)
        self.dct_panel.clear_image()
        self.dwt_panel.clear_image()
        self.image_info.setText(
            f"{Path(file_path).name} · {original_size[0]}×{original_size[1]} → 512×512 · відтінки сірого"
        )
        self.image_info.setToolTip(str(file_path))
        self.statusBar().showMessage("Зображення підготовлено. Пропорції збережено; вільні поля заповнено чорним.")
        return True
