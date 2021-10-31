import sys
import traceback as tb
import datetime

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QTimer, QModelIndex, QEvent, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QAbstractItemView, QPushButton, QLineEdit, QLabel, QCheckBox, \
    QWidget, QFrame, QInputDialog, QTextEdit, QSizePolicy, QPlainTextEdit, QComboBox, QSplashScreen

from classes.bb_converts import date_us_ru, date_ru_us
from classes.cl_logwriter import LogWriter
from classes.cl_statistics import Statistics
from classes.db_session import ConnectDb
from classes.t_journal import TJournalModel
from classes.cl_const import Const
from classes.t_tables import TRasp, TJournals, TUsers, TGroups, TGroupTable
from forms_journ.t_tab5 import Ui_tab5Form


def except_hook(cls, exception, traceback):
    global flog
    flog.to_log(f"""{exception} | \n{tb.format_tb(traceback)[0]}""")
    sys.__excepthook__(cls, exception, traceback)


class T5Window(QWidget, Ui_tab5Form):  # tab5 формы
    clicked_cancel = pyqtSignal()
    clicked_enter = pyqtSignal()

    def __init__(self, conn, user_id):
        self.logfile = LogWriter()
        if Const.TEST_MODE:
            self.logfile.to_log(f"""======>  Tab5. Start __init__""")
            print("======>  Tab5. Start __init__")
        super(T5Window, self).__init__()
        self.setupUi(self)
        self.con = conn
        self.user_id_preset = user_id
        self.user_id = self.user_id_preset
        self.edit_spisok = []
        self.txt_comment.hide()

        self.logfile = LogWriter()
        self.user = TUsers(self.con)
        self.groups = TGroups(self.con)
        self.user.set_filter( f'u.id = {self.user_id}')
        self.groups.set_filter( f"g.idUsers = {self.user_id} and c.year = {Const.YEAR}")
        # print(self.groups.data)
        self.group_table = TGroupTable(self.con)
        self.journ = TJournals(self.con)
        model = TJournalModel(self.journ, [1])
        self.tableView.setModel(model)
        self.stat = Statistics(self.con, self.user_id)
        self.installEventFilter(self)
        us = TUsers(self.con)
        spis = [(u[Const.USR_ID], u[Const.USR_NAME]) for u in us.data if u[Const.USR_PRIV][0] == '1']
        idx = -1
        for i, val in enumerate(spis):
            self.teach_spisok.addItem(f"{val[0]:4} : {val[1]}")
            if int(val[0]) == self.user_id:
                idx = i
        self.teach_spisok.currentIndexChanged.connect(self.change_teacher)
        self.teach_spisok.setCurrentIndex(idx)
        model.refresh_visual.connect(self.count_statistics)
        self.groupBox.currentIndexChanged.connect(self.change_current_group)
        self.tableView.doubleClicked.connect(self.start_edit_day)
        self.commitButton.clicked.connect(self.commit_action)
        self.rollbackButton.clicked.connect(self.commit_action)
        if Const.TEST_MODE:
            self.logfile.to_log(f"""======>  Tab5. Finish __init__""")
            print("======>  Tab5. Finish __init__")

    def change_teacher(self):
        self.tableView.model().beginResetModel()
        self.user_id = int(self.teach_spisok.currentText().split()[0])
        self.stat = Statistics(self.con, self.user_id)
        # self.stat.update()
        self.tableView.model().endResetModel()
        # self.count_statistics()
        self.activate()
        # print(self.user_id)

    def activate(self):
        self.tableView.model().beginResetModel()
        self.user.set_filter( f'u.id = {self.user_id}')
        self.groups.set_filter( f"g.idUsers = {self.user_id} and c.year = {Const.YEAR}")
        self.groupBox.clear()
        self.groupBox.setCurrentIndex(-1)
        if self.groups.rows() > 0:
            self.groupBox.insertItems(0, [f"{val[1]} : {val[7]}" for val in self.groups.data])
        else:
            self.journ.set_filter(f"j.idGroups = -1 and jc.year = {Const.YEAR}")
        self.tableView.model().endResetModel()
        self.change_current_group()
        self.count_statistics()
        # self.show()

    def commit_action(self):
        self.record_cursor = self.tableView.currentIndex().row()
        self.tableView.model().beginResetModel()
        if self.sender().objectName() == 'commitButton':
            self.journ.commit()
            self.stat.update()
        else:
            self.journ.rollback()
        self.journ.update()
        self.tableView.model().endResetModel()
        self.tableView.resizeColumnsToContents()
        # self.tableView.selectRow(0)
        self.tableView.setCurrentIndex(self.tableView.model().index(self.record_cursor, 0))
        self.tableView.setFocus()

    def eventFilter(self, object, event):
        if Const.IN_TRANSACTION and self.tableView.isEnabled():
            Const().to_commit(self.con)
            self.commitButton.show()
            self.rollbackButton.show()
        else:
            self.commitButton.hide()
            self.rollbackButton.hide()
        if Const.IN_TRANSACTION:
            Const().to_commit(self.con)
            self.frame_3.setStyleSheet("background-color: rgb(240, 212, 212);")
        else:
            self.frame_3.setStyleSheet("background-color: rgb(240, 240, 240);")

        if event.type() == QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Escape:
                self.clicked_cancel.emit()
            elif event.key() == QtCore.Qt.Key_Return:
                if self.tableView.isEnabled():
                    self.start_edit_day()
                else:
                    self.clicked_enter.emit()
            elif event.key() == QtCore.Qt.Key_F2:
                if self.commitButton.isVisible():
                    self.commitButton.click()
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

    def start_edit_day(self):
        self.labelHead.setDisabled(False)
        self.frame_2.setDisabled(True)
        self.tableView.setDisabled(True)
        self.record_cursor = self.tableView.currentIndex().row()
        if self.record_cursor < 0:
            return
        layoutCorr = self.letter_place.layout()
        layoutShape = self.shape_frame.layout()
        self.shape_frame.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        layoutCorr.setContentsMargins(20, 20, 20, 20)
        layoutCorr.setAlignment(QtCore.Qt.AlignCenter)
        self.txt_comment.show()
        self.txt_comment.setPlainText(self.journ.data[self.record_cursor][8])
        pos = 1

        preset = {'present': [], 'estim': [], 'shtraf': []}
        preset['present'] = list(map(int, (self.journ.data[self.record_cursor][Const.JRN_PRESENT]).split()))
        preset['estim'] = {val.split('=')[0]: val.split('=')[1] for val in (self.journ.data[self.record_cursor][Const.JRN_ESTIM]).split()}
        preset['shtraf'] = {val.split('=')[0]: val.split('=')[1] for val in (self.journ.data[self.record_cursor][Const.JRN_SHTRAF]).split()}

        posSh = 0
        le1 = QPlainTextEdit(self.journ.data[self.record_cursor][2])
        le1.setObjectName('lesson Name')
        le1.setMaximumHeight(50)
        self.edit_spisok.append(le1)
        layoutShape.addWidget(le1, posSh, 0, posSh + 1, 9)
        posSh += 1

        lb = QLabel('Начало:')
        lb.setMaximumWidth(100)
        self.edit_spisok.append(lb)
        layoutShape.addWidget(lb, posSh, 2)
        le = QLineEdit(self.journ.data[self.record_cursor][3])
        le.setMaximumWidth(100)
        le.setInputMask('00:00')
        le.setObjectName('lesson tStart')
        self.edit_spisok.append(le)
        layoutShape.addWidget(le, posSh, 3)
        le = QLineEdit(date_us_ru(self.journ.data[self.record_cursor][1]))
        le.setObjectName('lesson Date')
        le.setInputMask('00.00.0000')
        le.setMaximumWidth(100)
        self.edit_spisok.append(le)
        layoutShape.addWidget(le, posSh, 8)
        posSh += 1

        lb = QLabel('Окончание:')
        self.edit_spisok.append(lb)
        lb.setMaximumWidth(100)
        layoutShape.addWidget(lb, posSh, 2)
        le = QLineEdit(self.journ.data[self.record_cursor][4])
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
        btn.clicked.connect(self.end_edit_day)
        # btn.installEventFilter(self)
        btn.setObjectName('Save')
        self.clicked_enter.connect(btn.click)
        btn.setMinimumWidth(100)
        self.edit_spisok.append(btn)
        layoutShape.addWidget(btn, posSh, 7)
        btn = QPushButton('Отменить')
        btn.clicked.connect(self.end_edit_day)
        self.clicked_cancel.connect(btn.click)
        # btn.installEventFilter(self)
        btn.setObjectName('Cancel')
        btn.setMinimumWidth(100)
        self.edit_spisok.append(btn)
        layoutShape.addWidget(btn, posSh, 8)
        posSh += 2

        lb = QLabel('№')
        lb.setAlignment(QtCore.Qt.AlignCenter)
        self.edit_spisok.append(lb)
        layoutCorr.addWidget(lb, pos, 0)

        lb = QLabel('Фамилия И.О.')
        lb.setAlignment(QtCore.Qt.AlignCenter)
        self.edit_spisok.append(lb)
        layoutCorr.addWidget(lb, pos, 1)

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
        h_line = QFrame()
        h_line.setFrameShape(QFrame.HLine)
        layoutCorr.addWidget(h_line, pos, 0, pos + 1, 6)
        pos += 1
        lb = QLabel('')
        self.edit_spisok.append(lb)
        layoutCorr.addWidget(lb, pos, 3)
        pos += 2

        self.group_table.set_filter(
            f"g.id = {self.groups.data[self.groupBox.currentIndex()][0]} and jc.year = {Const.YEAR}")
        if self.group_table.rows() > 0:
            for i, user in enumerate(self.group_table.data):
                userId = self.group_table.data[i][4]
                lb = QLabel(f"{i + 1}")
                lb.setAlignment(QtCore.Qt.AlignCenter)
                lb.setMaximumWidth(30)
                self.edit_spisok.append(lb)
                layoutCorr.addWidget(lb, pos, 0)
                lb = QLabel(user[2])
                self.edit_spisok.append(lb)
                layoutCorr.addWidget(lb, pos, 1)
                lb = QLabel(' ')
                self.edit_spisok.append(lb)
                layoutCorr.addWidget(lb, pos, 2)
                chb = QCheckBox()
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
                oc.setMaximumWidth(110)
                oc.setObjectName(f"lesson {userId} shtraf")
                oc.setText(preset['shtraf'].get(str(userId), ''))
                self.edit_spisok.append(oc)
                layoutCorr.addWidget(oc, pos, 5)
                pos += 2
        le1.selectAll()
        le1.setFocus()

    def click_in_table(self):
        new_state = self.sender().isChecked()
        for chb in self.edit_spisok:
            if isinstance(chb, QCheckBox):
                chb.setChecked(new_state)

    def end_edit_day(self):
        to_save = self.sender().objectName() == 'Save'
        self.labelHead.setDisabled(True)
        self.frame_2.setDisabled(False)
        self.tableView.setDisabled(False)
        result_head = {'present': [], 'estim': [], 'shtraf': []}
        result_head['comment'] = self.txt_comment.toPlainText()
        self.txt_comment.hide()
        for wid in self.edit_spisok:
            if to_save:
                if 'lesson' in wid.objectName():
                    args = wid.objectName().split()
                    # if Const.TEST_MODE:
                    #     print(args)
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
                        if args[2] == 'estim':
                            if wid.text():
                                result_head['estim'].append(f'{args[1]}={wid.text().split()[0]}')
                        if args[2] == 'shtraf':
                            if wid.text():
                                result_head['shtraf'].append(f'{args[1]}={wid.text().split()[0]}')
            wid.deleteLater()
        if to_save:
            self.tableView.model().beginResetModel()
            id = self.journ.data[self.record_cursor][0]
            result_head['present'] = ' '.join(result_head['present'])
            result_head['estim'] = ' '.join(result_head['estim'])
            result_head['shtraf'] = ' '.join(result_head['shtraf'])
            self.journ.rec_update(id, result_head)
            self.journ.update()
            self.tableView.model().endResetModel()
            self.tableView.resizeColumnsToContents()
            self.tableView.setCurrentIndex(self.tableView.model().index(self.record_cursor, 0))
            # self.count_statistics()
        self.tableView.setFocus()
        self.edit_spisok.clear()

    def count_statistics(self):
        # self.lcdNumber_1.display(self.tableView.model().get_summa_present())
        stats = self.stat.get_statistics()
        self.lcd_year.display(stats['year'])
        self.lcd_cnt_stud.display(stats['cnt_stud'])
        self.lcd_cnt_grp.display(stats['cnt_grp'])
        self.lcd_cnt_week.display(stats['cnt_week'])
        self.lcd_h_to_week.display(stats['h_to_week'])
        self.lb_date_min.setText(date_us_ru(stats['date_min']))
        self.lb_date_max.setText(date_us_ru(stats['date_max']))

    def change_current_group(self):
        self.tableView.model().beginResetModel()
        self.tableView.selectRow(-1)
        if self.groups.rows() > 0:
            self.programName.setText(self.groups.data[self.groupBox.currentIndex()][2])
            self.journ.set_filter(
                f"j.idGroups = {self.groups.data[self.groupBox.currentIndex()][0]} and jc.year = {Const.YEAR}")
            self.tableView.selectRow(0)
        self.tableView.model().endResetModel()
        self.tableView.resizeColumnsToContents()
        row = 0
        date = datetime.date.today()
        for row in range(self.journ.rows()):
            if date < datetime.date.fromisoformat(date_ru_us(self.tableView.model().itemData(
                    self.tableView.model().index(row, 1))[0])):
                break
        # print(date_ru_us(self.tableView.model().itemData(self.tableView.model().index(row, 1))[0]))
        self.tableView.selectRow(row - 1)
        self.tableView.setFocus()


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    flog = LogWriter()


    con = ConnectDb('../settings.ini').get_con()
    wnd = T5Window(con, 19)
    wnd.showMaximized()
    sys.exit(app.exec())
