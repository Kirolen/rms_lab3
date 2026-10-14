import csv

from PySide6.QtWidgets import (
    QAbstractItemView, QDialog, QFileDialog, QHeaderView, QLabel,
    QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout,
)


HEADERS = ("Метод", "Зберегти, %", "Ненульових", "Усього", "Ненульових, %", "PSNR, дБ")


def result_values(result):
    return (
        result.method, str(result.percent), str(result.nonzero), str(result.total),
        f"{result.nonzero / result.total * 100:.2f}",
        "∞" if result.psnr == float("inf") else f"{result.psnr:.2f}",
    )


def save_results_csv(file_path, results):
    with open(file_path, "w", encoding="utf-8-sig", newline="") as output:
        writer = csv.writer(output, delimiter=";")
        writer.writerow(HEADERS)
        writer.writerows(result_values(result) for result in results)


class ExperimentDialog(QDialog):
    def __init__(self, results, image_name, parent=None):
        super().__init__(parent)
        self.results = results
        self.setWindowTitle("Порівняння DCT та DWT")
        self.resize(850, 420)
        layout = QVBoxLayout(self)
        label = QLabel(f"{image_name} · 512×512 · збереження 50%, 10% та 1% коефіцієнтів")
        label.setWordWrap(True)
        layout.addWidget(label)
        self.table = QTableWidget(len(results), len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for row, result in enumerate(results):
            for column, value in enumerate(result_values(result)):
                self.table.setItem(row, column, QTableWidgetItem(value))
        layout.addWidget(self.table)
        note = QLabel(
            "Більше PSNR — менша похибка. Ненульові коефіцієнти характеризують "
            "розрідженість, а не розмір закодованого файла."
        )
        note.setWordWrap(True)
        layout.addWidget(note)
        self.save_button = QPushButton("Зберегти таблицю CSV")
        self.save_button.clicked.connect(self._save_csv)
        layout.addWidget(self.save_button)

    def _save_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Зберегти результати", "experiments.csv", "CSV (*.csv)",
        )
        if not file_path:
            return
        try:
            save_results_csv(file_path, self.results)
        except OSError as error:
            QMessageBox.warning(self, "Помилка збереження", str(error))
