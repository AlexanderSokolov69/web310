import sys
import traceback as tb
import datetime

from PyQt5 import QtWidgets, QtCore, QtSql
from PyQt5.QtCore import QTimer, QModelIndex, QEvent, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QAbstractItemView, QPushButton, QLineEdit, QLabel, QCheckBox, \
    QWidget, QFrame, QInputDialog, QTextEdit, QSizePolicy, QPlainTextEdit, QComboBox, QSplashScreen

from classes.bb_converts import date_us_ru, date_ru_us
from classes.cl_logwriter import LogWriter
from classes.cl_statistics import Statistics
from classes.t_journal import TJournalModel
from classes.cl_const import Const
from classes.t_tables import TRasp, TJournals, TUsers, TGroups, TGroupTable
from forms_journ.t_tab5 import Ui_tab5Form
from widgets_prg.db_classes import QPrepod
from widgets_prg.t_db_session import QtConnectDb


def except_hook(cls, exception, traceback):
    global flog
    flog.to_log(f"""{exception} | \n{tb.format_tb(traceback)[0]}""")
    sys.__excepthook__(cls, exception, traceback)


class T5Window(QWidget, Ui_tab5Form):  # tab5 формы
    def __init__(self, conn, user_id):
        self.logfile = LogWriter()
        if Const.TEST_MODE:
            self.logfile.to_log(f"""======>  Tab5. Start __init__""")
            print("======>  Tab5. Start __init__")
        super(T5Window, self).__init__()
        self.setupUi(self)
        self.initUi(user_id)

    def initUi(self, user_id):
        self.user_id = user_id
        self.prepod = QPrepod()
        self.teach_spisok_list = []

        self.refresh_prepod_table1()
        if Const.TEST_MODE:
            self.logfile.to_log(f"""======>  Tab5. Finish __init__""")
            print("======>  Tab5. Finish __init__")

    def refresh_prepod_table(self):
        if self.prepod.refresh_select((Const.ACC_TEACHER,)):
            self.teach_spisok_list = []
            self.teach_spisok.clear()
            self.prepod.first()
            idx = -1
            while self.prepod.isValid():
                self.teach_spisok_list.append([self.prepod.value(Const.USR_ID),
                                               self.prepod.value(Const.USR_NAME)])
                self.teach_spisok.addItem(self.teach_spisok_list[-1][1])
                if self.teach_spisok_list[-1][0] == self.user_id:
                    idx = self.teach_spisok.currentIndex()
                self.prepod.next()
            self.teach_spisok.setCurrentIndex(idx)

    def refresh_prepod_table1(self):
        self.prepod.exec(self.prepod.on_prepare)
        self.prepod.first()
        print(self.prepod.value('Фамилия И.О.'))

    def refresh_rasp_table(self):
        pass

    def refresh_journal_table(self):
        pass


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    flog = LogWriter()

    spl = QSplashScreen(QPixmap('../Splash/Splash01-02.PNG'))
    spl.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
    spl.show()

    if QtConnectDb('../settings.ini').get_con():
        wnd = T5Window(None, 19)
        spl.finish(wnd)
        wnd.showMaximized()

    sys.exit(app.exec())
