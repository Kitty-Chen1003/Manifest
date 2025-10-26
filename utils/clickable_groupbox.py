from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QDialog, QTableWidget, QTableWidgetItem, QDialogButtonBox, QHeaderView, QGroupBox
from PyQt5.QtCore import Qt, pyqtSignal


class ClickableGroupBox(QGroupBox):
    clicked = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
