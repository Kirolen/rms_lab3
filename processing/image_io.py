from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QImageReader, QPainter


def load_grayscale_image(file_path, size=512):
    reader = QImageReader(str(file_path))
    reader.setAutoTransform(True)
    source = reader.read()
    if source.isNull():
        raise ValueError(reader.errorString() or "Не вдалося прочитати зображення")

    original_size = (source.width(), source.height())
    scaled = source.scaled(
        size, size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    canvas = QImage(size, size, QImage.Format.Format_RGB32)
    canvas.fill(QColor("black"))
    painter = QPainter(canvas)
    painter.drawImage((size - scaled.width()) // 2, (size - scaled.height()) // 2, scaled)
    painter.end()
    return canvas.convertToFormat(QImage.Format.Format_Grayscale8), original_size
