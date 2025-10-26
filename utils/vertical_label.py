from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt


# label竖直显示
class VerticalLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super(VerticalLabel, self).__init__(*args, **kwargs)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(self.palette().windowText().color())

        rect = self.rect()
        painter.translate(rect.bottomLeft())
        painter.rotate(-90)

        painter.drawText(0, 0, rect.height(), rect.width(), Qt.AlignCenter, self.text())

        painter.end()