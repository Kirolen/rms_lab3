from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)
from pathlib import Path
import numpy as np
from PySide6.QtCore import Qt

from processing.compression import retain_largest
from processing.metrics import calculate_psnr
from processing.experiments import run_experiments
from ui.experiment_dialog import ExperimentDialog
from processing.dct import forward_dct, inverse_dct
from processing.dwt import forward_haar, inverse_haar
from processing.image_io import (
    array_to_image,
    image_to_array,
    load_grayscale_image,
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
        self.dct_coefficients = None
        self.dwt_coefficients = None
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
        self.dct_button = QPushButton("Виконати DCT")
        self.dct_button.setEnabled(False)
        self.dct_button.clicked.connect(self.run_dct)
        self.dwt_button = QPushButton("Виконати DWT")
        self.dwt_button.setEnabled(False)
        self.dwt_button.clicked.connect(self.run_dwt)
        self.image_info = QLabel("Зображення не вибрано")
        self.image_info.setWordWrap(True)
        self.image_info.setObjectName("subtitle")
        toolbar = QHBoxLayout()
        toolbar.addWidget(self.open_button)
        toolbar.addWidget(self.dct_button)
        toolbar.addWidget(self.dwt_button)
        toolbar.addWidget(self.image_info, stretch=1)
        layout.addLayout(toolbar)

        self.compression_label = QLabel("Зберегти коефіцієнтів: 100%")
        self.compression_slider = QSlider(Qt.Orientation.Horizontal)
        self.compression_slider.setRange(1, 100)
        self.compression_slider.setValue(100)
        self.compression_slider.setEnabled(False)
        self.compression_slider.setTracking(False)
        self.compression_slider.valueChanged.connect(self._change_compression)
        compression_layout = QHBoxLayout()
        compression_layout.addWidget(self.compression_label)
        compression_layout.addWidget(self.compression_slider, stretch=1)
        layout.addLayout(compression_layout)
        self.experiment_button = QPushButton("Експеримент: 50% / 10% / 1%")
        self.experiment_button.setEnabled(False)
        self.experiment_button.clicked.connect(self._run_experiments)
        self.save_button = QPushButton("Зберегти результати PNG")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self._save_images)
        actions_layout = QHBoxLayout()
        actions_layout.addWidget(self.experiment_button)
        actions_layout.addWidget(self.save_button)
        layout.addLayout(actions_layout)

        self.original_panel = ImagePanel("Original", "Зображення не завантажено")
        self.original_panel.metrics_label.setText("Підготовлене зображення · 512×512 · 8 біт")
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
        self.dct_coefficients = None
        self.dwt_coefficients = None
        self.image_path = str(file_path)
        self.original_panel.set_image(image)
        self.dct_panel.clear_image()
        self.dwt_panel.clear_image()
        self.save_button.setEnabled(False)
        self.dct_button.setEnabled(True)
        self.dwt_button.setEnabled(True)
        self.compression_slider.setEnabled(True)
        self.experiment_button.setEnabled(True)
        self.image_info.setText(
            f"{Path(file_path).name} · {original_size[0]}×{original_size[1]} → 512×512 · відтінки сірого"
        )
        self.image_info.setToolTip(str(file_path))
        self.statusBar().showMessage("Зображення підготовлено. Пропорції збережено; вільні поля заповнено чорним.")
        return True

    def run_dct(self):
        if self.original_image is None:
            return
        original = image_to_array(self.original_image)
        self.dct_coefficients = forward_dct(original)
        filtered = retain_largest(self.dct_coefficients, self.compression_slider.value())
        restored = inverse_dct(filtered)
        self._show_result(self.dct_panel, restored, filtered)
        self.statusBar().showMessage(
            f"DCT: блоки 8×8. Збережено до {self.compression_slider.value()}% найбільших коефіцієнтів."
        )

    def run_dwt(self):
        if self.original_image is None:
            return
        original = image_to_array(self.original_image)
        self.dwt_coefficients = forward_haar(original)
        filtered = retain_largest(self.dwt_coefficients, self.compression_slider.value())
        restored = inverse_haar(filtered)
        self._show_result(self.dwt_panel, restored, filtered)
        self.statusBar().showMessage(
            f"DWT: Хаар, 3 рівні. Збережено до {self.compression_slider.value()}% найбільших коефіцієнтів."
        )

    def _change_compression(self, percent):
        self.compression_label.setText(f"Зберегти коефіцієнтів: {percent}%")
        if self.original_image is None:
            return
        if self.dct_coefficients is None:
            self.dct_coefficients = forward_dct(image_to_array(self.original_image))
        if self.dwt_coefficients is None:
            self.dwt_coefficients = forward_haar(image_to_array(self.original_image))
        dct_filtered = retain_largest(self.dct_coefficients, percent)
        dwt_filtered = retain_largest(self.dwt_coefficients, percent)
        self._show_result(self.dct_panel, inverse_dct(dct_filtered), dct_filtered)
        self._show_result(self.dwt_panel, inverse_haar(dwt_filtered), dwt_filtered)
        self.statusBar().showMessage(
            f"Збережено до {percent}% коефіцієнтів DCT і DWT. Решту обнулено."
        )

    def _show_result(self, panel, restored, coefficients):
        image = array_to_image(restored)
        panel.set_image(image)
        psnr = calculate_psnr(
            image_to_array(self.original_image), image_to_array(image),
        )
        panel.set_metrics(psnr, int(np.count_nonzero(coefficients)), coefficients.size)
        self.save_button.setEnabled(True)

    def _save_images(self):
        directory = QFileDialog.getExistingDirectory(self, "Папка для результатів")
        if directory:
            try:
                self.save_images(directory)
            except OSError as error:
                QMessageBox.warning(self, "Помилка збереження", str(error))

    def save_images(self, directory):
        percent = self.compression_slider.value()
        images = {"original.png": self.original_image}
        for name, panel in (("dct", self.dct_panel), ("dwt", self.dwt_panel)):
            if panel._image is not None:
                images[f"{name}_keep_{percent}.png"] = panel._image
        paths = [Path(directory) / name for name in images]
        if any(path.exists() for path in paths):
            raise OSError("У папці вже є результати з такими назвами. Виберіть іншу папку.")
        for name, image in images.items():
            if image is None or not image.save(str(Path(directory) / name), "PNG"):
                raise OSError(f"Не вдалося зберегти {name}")
        self.statusBar().showMessage(f"Збережено {len(images)} зображень у {directory}")

    def _run_experiments(self):
        if self.original_image is None:
            return
        results = run_experiments(image_to_array(self.original_image))
        dialog = ExperimentDialog(results, Path(self.image_path).name, self)
        dialog.exec()
