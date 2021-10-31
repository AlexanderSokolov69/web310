import os
import sys
import traceback as tb

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMainWindow, QVBoxLayout, QInputDialog

from classes.cl_const import Const
from classes.cl_logwriter import LogWriter
from new_prg.db_connect import TSqlQuery
from new_prg.main_form import Ui_NMainWindow
from new_prg.q_about import QAboutWnd
from new_prg.q_converts import get_prepod_list
from new_prg.q_tab4_prg import QTab4FormWindow
from new_prg.q_tab5_prg import QT5Window
from widgets_prg.t_db_session import QtConnectDb


def except_hook(cls, exception, traceback):
    global flog
    flog.to_log(f"""{exception} | \n{tb.format_tb(traceback)[0]}""")
    sys.__excepthook__(cls, exception, traceback)


class MainWindow(QMainWindow, Ui_NMainWindow):
    def __init__(self, user_id=None):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.initUi(user_id)

    def initUi(self, user_id=None):
        self.user_id = user_id
        self.setWindowTitle('Кубышка (it-куб. Белая Холуница)')
        self.wnd = QAboutWnd()
        self.action_rasp.triggered.connect(self._change_to_rasp)
        self.action_journ.triggered.connect(self._change_to_journ)
        self.action_help.triggered.connect(self.wnd.show)
        self.menu.setStyleSheet("font: 11pt \"MS Shell Dlg 2\";")
        self.menu_users.setStyleSheet("font: 11pt \"MS Shell Dlg 2\";")
        users = get_prepod_list()
        for user in users:
            act = QtWidgets.QAction(self)
            act.setObjectName(f"{user[0]}")
            act.setText(f"{user[1]}")
            act.setCheckable(True)
            if user[0] == self.user_id:
                act.setChecked(True)
            else:
                act.setChecked(False)
            self.menu_users.addAction(act)
        self.menu_users.triggered.connect(self._change_current_user_id)
        if Const.TEST_MODE:
            print('self.user_id:', self.user_id)
        self.win_1 = QTab4FormWindow(int(self.user_id))
        self.win_1.message_out.connect(self._show_message)
        self.setCentralWidget(QT5Window(int(self.user_id)))

    def _show_message(self, msg):
        if Const.TEST_MODE:
            print('statusBar print', msg)
        # self.statusbar.show()
        self.statusbar.setStyleSheet("color: rgb(240, 40, 40);font: 12pt \"MS Shell Dlg 2\";")
        self.statusbar.showMessage(msg, 10000)

    def _change_current_user_id(self, action):
        new_user = action.objectName()
        for obj in self.menu_users.actions():
            if obj.objectName() == new_user:
                obj.setChecked(True)
            else:
                obj.setChecked(False)
        self.user_id = int(new_user)
        self.setCentralWidget(QT5Window(int(self.user_id)))

    def _change_to_rasp(self):
        self.win_1 = QTab4FormWindow(int(self.user_id))
        self.win_1.message_out.connect(self._show_message)
        self.setCentralWidget(self.win_1)

    def _change_to_journ(self):
        self.setCentralWidget(QT5Window(int(self.user_id)))


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    flog = LogWriter()

    spl = QSplashScreen(QPixmap('Splash/Splash01-02.PNG'))
    spl.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
    spl.show()

    if QtConnectDb('settings.ini').get_con():
        if Const.TEST_MODE:
            print('Connect: Ok')
        spl.showMessage(f"Login user: '{os.getlogin()}'", Qt.AlignBottom | Qt.AlignCenter, QColor('black'))
        sql = f"select id from users where winlogin = '{os.getlogin()}'"
        user = TSqlQuery().query_one_to_list(sql)
        if Const.TEST_MODE:
            print('Logged as:', user)
            print(f"select id from users where winlogin = '{os.getlogin()}'")
        if user:
            spl.showMessage(f"Logged as: {user[0]}", Qt.AlignBottom | Qt.AlignCenter, QColor('black'))
            wnd = MainWindow(user[0])
        else:
            spl.showMessage(f"Пользователь не определен", Qt.AlignBottom | Qt.AlignCenter, QColor('black'))
            wnd = MainWindow(-1)
        spl.finish(wnd)
        wnd.showMaximized()
    sys.exit(app.exec())
