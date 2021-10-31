import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget

from new_prg.about_wnd import Ui_AboutForm


class QAboutWnd(QWidget, Ui_AboutForm):
    def __init__(self):
        super(QAboutWnd, self).__init__()
        self.setupUi(self)
        self.initUi()

    def initUi(self):
        self.setFixedSize(800, 600)
        self.setWindowModality(Qt.WindowModal)
        with open('readme.txt', encoding='utf8') as r:
            self.text.setStyleSheet("font: 11pt \"MS Shell Dlg 2\";")
            self.text.setText(r.read())
        self.setWindowFlag(Qt.WindowStaysOnTopHint | Qt.WindowModal)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = QAboutWnd()
    app.exec()
