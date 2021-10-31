import sqlite3
import sys
import traceback as tb
import datetime

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QTimer, QModelIndex, QEvent, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QApplication, QAbstractItemView, QPushButton, QLineEdit, QLabel, QCheckBox, \
    QWidget, QFrame, QInputDialog

from classes.bb_converts import date_us_ru, date_ru_us
from classes.cl_logwriter import LogWriter
from classes.cl_statistics import Statistics
from classes.db_session import ConnectDb
from classes.t_journal import TJournalModel
from classes.cl_const import Const
from classes.t_tables import TRasp, TJournals, TUsers, TGroups, TGroupTable
from forms_journ.t_tab6 import Ui_tab6Form


def except_hook(cls, exception, traceback):
    global flog
    flog.to_log(f"""{exception} | \n{tb.format_tb(traceback)[0]}""")
    sys.__excepthook__(cls, exception, traceback)


class T6Window(QWidget, Ui_tab6Form):  # tab5 формы
    def __init__(self, con, user_id):
        super(T6Window, self).__init__()
        self.setupUi(self)

        self.boxYear.insertItems(0, ['2020', '2021', '2022'])
        self.boxYear.setCurrentIndex(Const.YEAR - 2020)
        self.boxYear.currentIndexChanged.connect(self.changed_main_year)
        self.dateStart.setDate(datetime.date.fromisoformat(Const.D_START))
        self.dateEnd.setDate(datetime.date.fromisoformat(Const.D_END))

        self.stat = Statistics(con, 15)
        self.struct = self.stat.get_full_structure()
        # self.prn_struct(self.struct, 0)

    def prn_struct(self, struct: dict, tab=0):
        for el in struct.keys():
            if isinstance(struct[el], dict):
                print(f"{'    ' * tab} <{el}>:")
                self.prn_struct(struct[el], tab + 1)
            else:
                print('    ' * tab, el)
        print()


    def changed_main_year(self):
        Const.YEAR = int(self.boxYear.currentText())
        self.stat.update()


#
if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    flog = LogWriter()
    con = sqlite3.connect("../db/database_J.db")  # ConnectDb('..db/databases_j.db').get_con()
    wnd = T6Window(con, 19)
    wnd.showMaximized()
    sys.exit(app.exec())
