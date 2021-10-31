import sys
import os
import traceback as tb
import datetime

from PyQt5 import QtWidgets, QtCore, QtSql, QtGui
from PyQt5.QtCore import QTimer, QModelIndex, QEvent, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtSql import QSqlQueryModel, QSqlQuery
from PyQt5.QtWidgets import QMainWindow, QApplication, QAbstractItemView, QPushButton, QLineEdit, QLabel, QCheckBox, \
    QWidget, QFrame, QInputDialog, QTextEdit, QSizePolicy, QPlainTextEdit, QComboBox, QSplashScreen

from classes.bb_converts import date_us_ru, date_ru_us
from classes.cl_logwriter import LogWriter
from classes.cl_const import Const
from forms_journ.t_tab5 import Ui_tab5Form
from new_prg.db_connect import QUsers, QGroups, QJournals, QGroupTables, TSqlQuery, QStatisticsOne
from new_prg.q_models import QTableModel, JournQTableModel
from widgets_prg.t_db_session import QtConnectDb


def except_hook(cls, exception, traceback):
    global flog
    flog.to_log(f"""{exception} | \n{tb.format_tb(traceback)[0]}""")
    sys.__excepthook__(cls, exception, traceback)


class QT5Window(QWidget, Ui_tab5Form):  # tab5 формы
    clicked_cancel = pyqtSignal()
    clicked_enter = pyqtSignal()
    message_out = pyqtSignal()

    def __init__(self, user_id):
        self.logfile = LogWriter()
        if Const.TEST_MODE:
            self.logfile.to_log(f"""======>  Tab5. Start __init__""")
            print("======>  Tab5. Start __init__")
        super(QT5Window, self).__init__()
        self.setupUi(self)
        self.initUi(user_id)

    def initUi(self, user_id=None):
        self.label_4.hide()
        self.label_5.hide()
        self.label_6.hide()
        self.lcd_cnt_stud.hide()
        self.lcd_cnt_grp.hide()
        self.lcd_cnt_week.hide()
        self.user_id = user_id
        self.in_user_id = user_id
        self.edit_spisok = []
        self.groupBox.hide()
        self.txt_comment.hide()
        self.edited_record = None
        self.commitButton.hide()
        self.rollbackButton.hide()
        self.tableView.setStyleSheet("font: 11pt \"MS Shell Dlg 2\";")

        self.teach = QUsers(params=(Const.ACC_PREPOD, ), dsort=('u.name', ))
        self.groups = QGroups(dsort=('g.name',))
        self.journ = QJournals(params=(-1, ), dsort=('j.date',))
        self.gtable =  QGroupTables(dsort=('u.name',))
        self.stat_hours = QStatisticsOne()

        self.installEventFilter(self)
        self.groupBox.currentIndexChanged.connect(self.journf_refresh_sql)
        self.tableView.doubleClicked.connect(self.journf_start_edit_day)
        self.commitButton.clicked.connect(TSqlQuery.commit_table)
        self.rollbackButton.clicked.connect(TSqlQuery.rollback_table)

        self.teach_spisok.currentIndexChanged.connect(self.groupsf_refresh_sql)
        if Const.TEST_MODE:
            self.logfile.to_log(f"""======>  Tab5. Finish __init__""")
            print("======>  Tab5. Finish __init__")

    def journf_start_edit_day(self):
        data: QTableModel = self.tableView.model()
        record = data.sql_obj.cache[self.tableView.currentIndex().row()]
        self.edited_record = record[Const.JRN_ID]

        self.labelHead.setDisabled(False)
        self.frame_2.setDisabled(True)
        self.tableView.setDisabled(True)
#
        MaxWidth = 800
        layoutCorr = self.letter_place.layout()
        layoutShape = self.shape_frame.layout()
        self.shape_frame.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        layoutCorr.setContentsMargins(20, 20, 20, 20)
        layoutCorr.setAlignment(QtCore.Qt.AlignCenter)
        self.txt_comment.show()
        self.txt_comment.setPlainText(record[Const.JRN_COMMENT])
        self.txt_comment.setMinimumWidth(MaxWidth)
        pos = 1
#
        preset = {'present': list(map(int, (record[Const.JRN_PRESENT].split()))),
                  'estim': {val.split('=')[0]: val.split('=')[1].strip() for val in
                            record[Const.JRN_ESTIM].split()},
                  'shtraf': {val.split('=')[0]: val.split('=')[1].strip() for val in
                             record[Const.JRN_SHTRAF].split()},
                  'usercomm': {val.split('=')[0]: val.split('=')[1].strip() for val in
                             record[Const.JRN_USRCOMM].split()}
                  }
        # print(preset)
        #
        posSh = 0
        le1 = QPlainTextEdit(record[Const.JRN_THEME])
        le1.setObjectName('lesson Name')
        le1.setMaximumHeight(50)
        le1.setTabChangesFocus(True)
        self.edit_spisok.append(le1)
        layoutShape.addWidget(le1, posSh, 0, posSh + 1, 9)
        posSh += 1
#
        lb = QLabel('Начало:')
        lb.setMaximumWidth(100)
        self.edit_spisok.append(lb)
        layoutShape.addWidget(lb, posSh, 2)
        le = QLineEdit(record[Const.JRN_START])
        le.setMaximumWidth(100)
        le.setInputMask('00:00')
        le.setObjectName('lesson tStart')
        self.edit_spisok.append(le)
        layoutShape.addWidget(le, posSh, 3)
        le = QLineEdit(date_us_ru(record[Const.JRN_DATE]))
        le.setObjectName('lesson Date')
        le.setInputMask('00.00.0000')
        le.setMaximumWidth(100)
        self.edit_spisok.append(le)
        layoutShape.addWidget(le, posSh, 8)
        posSh += 1
#
        lb = QLabel('Окончание:')
        self.edit_spisok.append(lb)
        lb.setMaximumWidth(100)
        layoutShape.addWidget(lb, posSh, 2)
        le = QLineEdit(record[Const.JRN_END])
        le.setMaximumWidth(100)
        le.setInputMask('00:00')
        le.setObjectName('lesson tEnd')
        self.edit_spisok.append(le)
        layoutShape.addWidget(le, posSh, 3)
        lb = QLabel(' ')
        self.edit_spisok.append(lb)
        lb.setMinimumWidth(30)
        layoutShape.addWidget(lb, posSh, 6)
        btn = QPushButton('Сохранить')
        btn.clicked.connect(self.journf_end_edit_day)
        btn.setObjectName('Save')
        btn.setMinimumWidth(100)
        self.clicked_enter.connect(btn.click)
        self.edit_spisok.append(btn)
        layoutShape.addWidget(btn, posSh, 7)
        btn = QPushButton('Отменить')
        btn.clicked.connect(self.journf_end_edit_day)
        # self.clicked_cancel.connect(btn.click)
        # btn.installEventFilter(self)
        btn.setObjectName('Cancel')
        btn.setMinimumWidth(100)
        self.clicked_cancel.connect(btn.click)
        self.edit_spisok.append(btn)
        layoutShape.addWidget(btn, posSh, 8)
        posSh += 2
#
        lb = QLabel('№')
        lb.setAlignment(QtCore.Qt.AlignCenter)
        self.edit_spisok.append(lb)
        layoutCorr.addWidget(lb, pos, 0)

        lb = QLabel('Фамилия И.О.')
        lb.setAlignment(QtCore.Qt.AlignCenter)
        self.edit_spisok.append(lb)
        layoutCorr.addWidget(lb, pos, 1)
#
        lb = QCheckBox('')
        lb.stateChanged.connect(self.click_in_table)
        self.edit_spisok.append(lb)
        layoutCorr.addWidget(lb, pos, 3)

        lb = QLabel('Оценка')
        lb.setAlignment(QtCore.Qt.AlignCenter)
        self.edit_spisok.append(lb)
        layoutCorr.addWidget(lb, pos, 4)

        lb = QLabel('Рейтинг')
        lb.setAlignment(QtCore.Qt.AlignCenter)
        self.edit_spisok.append(lb)
        layoutCorr.addWidget(lb, pos, 5)

        lb = QLabel('Коммент.')
        lb.setAlignment(QtCore.Qt.AlignCenter)
        self.edit_spisok.append(lb)
        layoutCorr.addWidget(lb, pos, 6)

        h_line = QFrame()
        h_line.setFrameShape(QFrame.HLine)
        layoutCorr.addWidget(h_line, pos, 0, pos + 1, 7)

        pos += 1
        lb = QLabel('')
        self.edit_spisok.append(lb)
        layoutCorr.addWidget(lb, pos, 3)
        pos += 2

        self.gtable.set_param_str((record[Const.JRN_IDG], ))
        self.gtable.refresh_select()
        for i in range(len(self.gtable.cache)):
            val = self.gtable.cache[i]
            userId = val[Const.QGT_IDU]
            lb = QLineEdit(f"{i + 1}")
            lb.setReadOnly(True)
            if val[Const.QGT_NAVIGATOR][0] in '1':
                lb.setStyleSheet("background-color: rgb(240, 240, 240);font: 12pt \"MS Shell Dlg 2\";")
            else:
                lb.setStyleSheet("color: rgb(170, 0, 0);background-color: rgb(240, 240, 240);"
                                 "font: 12pt \"MS Shell Dlg 2\";")
            lb.setAlignment(QtCore.Qt.AlignCenter)
            lb.setMaximumWidth(30)
            self.edit_spisok.append(lb)
            layoutCorr.addWidget(lb, pos, 0)
            lb = QLineEdit(val[Const.QGT_STUDNAME].strip())
            lb.setReadOnly(True)
            if val[Const.QGT_NAVIGATOR][0] in '1':
                lb.setStyleSheet("background-color: rgb(240, 240, 240);font: 12pt \"MS Shell Dlg 2\";")
            else:
                lb.setStyleSheet("color: rgb(170, 0, 0);background-color: rgb(240, 240, 240);"
                                 "font: 12pt \"MS Shell Dlg 2\";")
            # lb.setMinimumWidth(300)
            lb.setAlignment(QtCore.Qt.AlignLeft)
            self.edit_spisok.append(lb)
            layoutCorr.addWidget(lb, pos, 1)
            lb = QLabel(' ')
            # lb.setMinimumWidth(50)
            self.edit_spisok.append(lb)
            layoutCorr.addWidget(lb, pos, 2)
            chb = QCheckBox()
            # chb.setMinimumWidth(40)
            chb.setMaximumWidth(40)
            chb.setObjectName(f"lesson {userId} check")
            chb.setChecked(userId in preset['present'])
            self.edit_spisok.append(chb)
            layoutCorr.addWidget(chb, pos, 3)
            oc = QLineEdit()
            oc.setMaximumWidth(60)
            oc.setObjectName(f"lesson {userId} estim")
            oc.setText(preset['estim'].get(str(userId), ''))
            self.edit_spisok.append(oc)
            layoutCorr.addWidget(oc, pos, 4)
            oc = QLineEdit()
            oc.setMaximumWidth(100)
            oc.setObjectName(f"lesson {userId} shtraf")
            oc.setText(preset['shtraf'].get(str(userId), ''))
            self.edit_spisok.append(oc)
            layoutCorr.addWidget(oc, pos, 5)
            oc = QLineEdit()
            oc.setMaximumWidth(150)
            oc.setObjectName(f"lesson {userId} usercomm")
            oc.setText(preset['usercomm'].get(str(userId), ''))
            self.edit_spisok.append(oc)
            layoutCorr.addWidget(oc, pos, 6)
            pos += 2
        le1.selectAll()
        le1.setFocus()

    def journf_end_edit_day(self):
        to_save = self.sender().objectName() == 'Save'
        self.labelHead.setDisabled(True)
        self.frame_2.setDisabled(False)
        self.tableView.setDisabled(False)
        result_head = {'present': [],
                       'estim': [],
                       'shtraf': [],
                       'usercomm': [],
                       'comment': self.txt_comment.toPlainText().strip()}
        self.txt_comment.hide()
        for wid in self.edit_spisok:
            if to_save:
                if 'lesson' in wid.objectName():
                    args = wid.objectName().split()
                    if len(args) == 2:
                        if args[1] == 'Date':
                            result_head[args[1]] = date_ru_us(wid.text())
                        elif args[1] == 'Name':
                            result_head[args[1]] = f'{wid.toPlainText()}'
                        else:
                            result_head[args[1]] = f'{wid.text()}'
                    elif len(args) == 3:
                        if args[2] == 'check':
                            if wid.isChecked():
                                result_head['present'].append(args[1])
                        elif args[2] == 'estim':
                            if wid.text():
                                result_head['estim'].append(f'{args[1]}={wid.text().split()[0]}')
                        elif args[2] == 'shtraf':
                            if wid.text():
                                result_head['shtraf'].append(f'{args[1]}={wid.text().split()[0]}')
                        elif args[2] == 'usercomm':
                            if wid.text():
                                result_head['usercomm'].append(f'{args[1]}={wid.text().split()[0]}')
            wid.deleteLater()
        if to_save:
            result_head['present'] = (' '.join(result_head['present'])).strip()
            result_head['estim'] = (' '.join(result_head['estim'])).strip()
            result_head['shtraf'] = (' '.join(result_head['shtraf'])).strip()
            result_head['usercomm'] = (' '.join(result_head['usercomm'])).strip()
            if self.edited_record:
                self.journ.rec_update(self.edited_record, result_head)
            self.journf_refresh_sql()
        self.tableView.setFocus()
        self.edit_spisok.clear()

    def click_in_table(self, state):
        for chb in self.edit_spisok:
            head = chb.objectName().split()
            if len(head) == 3 and head[2] == 'check':
                chb.setChecked(state == 2)

    def showEvent(self, a0: QtGui.QShowEvent) -> None:
        self.teachf_refresh_sql()

    def activate_window(self):
        pass

    def groupsf_refresh_sql(self):
        self.programName.setText('')
        if self.teach_spisok:  # self.teach_spisok.currentIndex() > 0:
            if Const.TEST_MODE:
                print(f"self.teach_spisok.count: {self.teach_spisok.count()}")
            try:
                pre_id = int(self.teach_spisok.currentText().split()[0])
            except IndexError:
                pre_id = -1
            # if self.in_user_id < 0:
            #     self.teach_spisok.removeItem(0)
            self.in_user_id = pre_id
            self.groups.set_param_str((Const.YEAR, self.in_user_id))
            self.groupBox.clear()
            if self.groups.refresh_select():
                self.groups.first()
                idx = -1
                while self.groups.isValid():
                    try:
                        self.groupBox.addItem(f"{self.groups.value(Const.GRP_ID):4} : "
                                              f"{self.groups.value(Const.GRP_NAME)} : "
                                              f"{self.groups.value(Const.GRP_COMMENT)}")
                    except IndexError:
                        pass
                    self.groups.next()
                self.groupBox.setCurrentIndex(0)
        self.statf_teacher_refresh()

    def teachf_refresh_sql(self):
        self.teach_spisok.clear()
        self.teach_spisok.addItem('')
        if self.teach.refresh_select():
            self.groupBox.hide()
            self.teach.first()
            idx = -1
            while self.teach.isValid():
                self.teach_spisok.addItem(f"{self.teach.value(Const.USR_ID):4} : {self.teach.value(Const.USR_NAME)}")
                if self.user_id == self.teach.value(Const.USR_ID):
                    idx = self.teach.at() + 1
                self.teach.next()
            self.teach_spisok.setCurrentIndex(idx)
            self.groupBox.show()

    def statf_teacher_refresh(self):
        self.stat_hours.set_param_str((Const.YEAR, self.in_user_id))
        self.stat_hours.refresh_select()
        if Const.TEST_MODE:
            print(self.in_user_id, self.stat_hours.cache)
        self.lcd_h_to_week.display(0 if len(self.stat_hours.cache[0]) == 0 else
                                   self.stat_hours.cache[0][0])

    def journf_refresh_sql(self):
        if self.groupBox.currentIndex() >= 0:
            grp = int(self.groupBox.currentText().split()[0])
            for i in range(len(self.groups.cache)):
                if self.groups.cache[i][Const.GRP_ID] == grp:
                    self.programName.setText(self.groups.cache[i][Const.GRP_CNAME])
                    break
            self.journ.set_param_str((grp, ))
            self.journ.refresh_select()
            model =  JournQTableModel(self.journ)
            self.tableView.setModel(model)
            self.tableView.model().beginResetModel()
            self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
            # self.tableView.setMaximumWidth(800)
            self.tableView.model().endResetModel()
            self.tableView.hideColumn(Const.JRN_ID)
            self.tableView.hideColumn(Const.JRN_ESTIM)
            self.tableView.hideColumn(Const.JRN_SHTRAF)
            self.tableView.hideColumn(Const.JRN_USRCOMM)
            self.tableView.hideColumn(Const.JRN_IDG)
            self.tableView.resizeColumnsToContents()
            dd = datetime.date.today()
            self.statf_refresh()
            for i in range(len(self.journ.cache)):
                # print(i, datetime.date.fromisoformat(self.journ.cache[i][Const.JRN_DATE]))
                if dd <= datetime.date.fromisoformat(self.journ.cache[i][Const.JRN_DATE]):
                    self.tableView.setCurrentIndex(self.tableView.model().index(i - 1, 0))
                    # print('break')
                    break
                else:
                    self.tableView.setCurrentIndex(self.tableView.model().index(i, 0))
            self.tableView.setFocus()
        else:
            self.tableView.setModel(None)

    def statf_refresh(self):
        self.lb_date_min.setText(date_us_ru(min([str(val[Const.JRN_DATE]) for val in self.journ.cache])))
        self.lb_date_max.setText(date_us_ru(max([str(val[Const.JRN_DATE]) for val in self.journ.cache])))
        self.lcd_year.display(Const.YEAR)

    def eventFilter(self, object, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Escape:
                self.clicked_cancel.emit()
            elif event.key() == QtCore.Qt.Key_Return:
                if self.tableView.isEnabled():
                    self.journf_start_edit_day()
                else:
                    self.clicked_enter.emit()
            else:
                res = True
                for n in dir(QtCore.Qt):
                    if eval(f'QtCore.Qt.{n}') == event.key():
                        if Const.TEST_MODE:
                            self.logfile.to_log(f""" Key pressed: {f'QtCore.Qt.{n}'} - {object}""")
                        res = False
                else:
                    if res:
                        if Const.TEST_MODE:
                            self.logfile.to_log(f""" Key pressed: {event.key()} - {object}""")
        return False


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    flog = LogWriter()

    spl = QSplashScreen(QPixmap('../Splash/Splash01-02.PNG'))
    spl.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
    spl.show()

    # conn_str = 'Driver=SQL Server;Server=172.16.1.12,1433;Database=Journal4303;UID=sa;PWD=Prestige2011!;'
    # db =  QtSql.QSqlDatabase.addDatabase('QODBC')
    # db.setDatabaseName(conn_str)
    # if db.open():

    if QtConnectDb('../settings.ini').get_con():
        if Const.TEST_MODE:
            print('Connect: Ok')
        qsql = QSqlQuery()
        qsql.exec(f"select id from users where winlogin = '{os.getlogin()}'")
        qsql.first()
        wnd = QT5Window(int(qsql.record().value(0)))
        spl.finish(wnd)
        wnd.show()
    sys.exit(app.exec())
