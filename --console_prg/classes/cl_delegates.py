from PyQt5 import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QItemDelegate
from classes.cl_const import Const


class Delegate(QItemDelegate):
    def __init__(self):
        super().__init__()
        self.filter = ''

    def paint(self, painter, option, index):
        row, col, txt = index.row(), index.column(), index.data()
        if self.filter and self.filter in txt:
            painter.setBrush(QBrush(Qt.yellow))
            painter.drawRect(option.rect)
        self.drawDisplay(painter, option, option.rect, txt)
