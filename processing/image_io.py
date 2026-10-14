from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QImageReader, QPainter
import numpy as np


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


def image_to_array(image):
    grayscale = image.convertToFormat(QImage.Format.Format_Grayscale8)
    rows = np.frombuffer(grayscale.constBits(), dtype=np.uint8).reshape(
        grayscale.height(), grayscale.bytesPerLine(),
    )
    return rows[:, :grayscale.width()].astype(np.float64)


def array_to_image(values):
    pixels = np.ascontiguousarray(np.clip(np.rint(values), 0, 255), dtype=np.uint8)
    height, width = pixels.shape
    return QImage(
        pixels.data, width, height, pixels.strides[0],
        QImage.Format.Format_Grayscale8,
    ).copy()
