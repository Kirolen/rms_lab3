from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class ImagePanel(QFrame):
    def __init__(self, title, placeholder, parent=None):
        super().__init__(parent)
        self.setObjectName("imagePanel")
        self._image = None
        self._placeholder = placeholder

        title_label = QLabel(title)
        title_label.setObjectName("panelTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.image_label = QLabel(placeholder)
        self.image_label.setObjectName("imagePreview")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setWordWrap(True)
        self.image_label.setMinimumSize(200, 260)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.addWidget(title_label)
        layout.addWidget(self.image_label, stretch=1)
        self.metrics_label = QLabel("PSNR: — | Коефіцієнти: —")
        self.metrics_label.setWordWrap(True)
        self.metrics_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.metrics_label)

    def set_metrics(self, psnr, count, total):
        quality = "∞" if psnr == float("inf") else f"{psnr:.2f} дБ"
        self.metrics_label.setText(
            f"PSNR: {quality}\nНенульові коефіцієнти: {count:,} / {total:,} ({count / total * 100:.2f}%)"
        )

    def set_image(self, image):
        self._image = image.copy()
        self._update_preview()

    def clear_image(self):
        self._image = None
        self.image_label.clear()
        self.image_label.setText(self._placeholder)
        self.metrics_label.setText("PSNR: — | Коефіцієнти: —")

    def _update_preview(self):
        if self._image is None:
            return
        available = self.image_label.contentsRect().size()
        available.setWidth(max(1, available.width() - 34))
        available.setHeight(max(1, available.height() - 34))
        self.image_label.setPixmap(QPixmap.fromImage(self._image).scaled(
            available,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_preview()
