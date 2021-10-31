import os
import sys
import sqlite3

from PyQt5.QtCore import pyqtSignal, Qt, QEvent, QObject, QRect
from PyQt5.QtGui import QPixmap
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtWidgets import QWidget, QApplication, QAbstractItemView, QGridLayout, QLabel, \
    QFrame, QButtonGroup, QSizePolicy, QPushButton, QComboBox, QLineEdit, QSplashScreen
from PyQt5 import QtCore

from classes.cl_const import Const
from classes.cl_journals import Journals
from classes.cl_logwriter import LogWriter
from classes.cl_rasp import Rasp
from classes.cl_users import Users
from classes.qt__classes import QLabelClk
from forms_journ.t_tab4 import Ui_tab4Form
from new_prg.db_connect import QRasp, QJournals, QUsers
from new_prg.q_converts import *
from new_prg.q_models import RaspQTableModel, JournQTableModel
from widgets_prg.t_db_session import QtConnectDb


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class QTab4FormWindow(QWidget, Ui_tab4Form):
    FONT_SIZE = 9
    collisium = pyqtSignal()
    LABEL_OK = '[   ]'
    LABEL_FREE = ' ' * 3
    LABEL_COLL = 'XXX'
    IDGROUPS_POS = 9
    IDDAY_POS = 10
    START_POS = 4
    END_POS = 5
    clicked_cancel = pyqtSignal()
    clicked_enter = pyqtSignal()
    message_out = pyqtSignal(str)

    def __init__(self, user_id=None):
        super(QTab4FormWindow, self).__init__()
        self.setupUi(self)
        self.initUi(user_id)

    def initUi(self, user_id):
        """
        Начальная настройка формы работы с расписанием
        :param con: указатель на БД SQL
        :return:
        """
        self.user_id = user_id
        self.con = None
        self.days_lst = qget_day_list()
        self.short_days_lst = qget_short_day_list()
        self.kab_lst = qget_kab_list()
        self.time_lst = qget_time_list()
        self.chk_buttonGroup = QButtonGroup(self)
        calend = []
        self.slots_dic = {}
        self.id = -1
        self.current_data = []
        self.new_preset = dict()
        self.edit_widgets = []
        self.h_layout_table.addWidget(QLabel())
        for nday in range(len(self.days_lst)):
            calend.append(self.create_day(nday))
            self.h_layout_table.addLayout(calend[-1])

        self.rasp = QRasp(params=(Const.YEAR, ), dsort=('[День]', 'k.name', 'r.tstart'))
        self.journ = QJournals(dsort=('[Дата]', '[Время нач.]'))

        self.tab4_add_btn.setVisible(False)
        self.tab4_edit_btn.setVisible(False)
        self.tab4_del_btn.setVisible(False)
        # self.tab4_add_btn.clicked.connect(self.group_clicked)
        # self.tab4_edit_btn.clicked.connect(self.group_clicked)
        # self.tab4_del_btn.clicked.connect(self.group_clicked)
        self.tab4_commit_btn.clicked.connect(self.group_clicked)
        self.tab4_rollback_btn.clicked.connect(self.group_clicked)

        self.tab4_lmonts.clear()
        spis = [f"""{val[0]} : {val[1]}""" for val in qget_monts_list()]
        self.tab4_lmonts.insertItem(0, '')
        self.tab4_lmonts.addItems(spis)
        self.tab4_lmonts.setCurrentIndex(0)

        self.flt_user.currentIndexChanged.connect(self.rasp_set_filter)
        self.flt_day.currentIndexChanged.connect(self.rasp_set_filter)
        self.flt_kab.currentIndexChanged.connect(self.rasp_set_filter)

        self.flt_user.clear()
        self.flt_user.insertItem(0, '')
        spis = QUsers(params=(Const.ACC_PREPOD, ), dsort=('u.name', ))
        spis.refresh_select()
        keys = [val[:][0] for val in spis.cache]
        # print(keys)
        try:
            id = keys.index(self.user_id)
        except ValueError:
            id = -1
        self.flt_user.addItems([f"{val[:][0]:4} : {val[:][1]}" for val in spis.cache])
        self.flt_user.setCurrentIndex(id + 1)
        self.flt_day.insertItem(0, '')
        self.flt_day.addItems(self.days_lst)
        self.flt_day.setCurrentIndex(0)
        self.flt_kab.insertItem(0, '')
        self.flt_kab.addItems([s[0] for s in self.kab_lst])
        self.flt_kab.setCurrentIndex(0)

        self.tab4_rasp_view.setStyleSheet("font: 11pt \"MS Shell Dlg 2\";")
        self.tab4_rasp_view.setModel(RaspQTableModel(self.rasp))
        self.tab4_rasp_view.hideColumn(Const.RSP_ID)
        self.tab4_rasp_view.hideColumn(Const.RSP_CNTLESS)
        self.tab4_rasp_view.hideColumn(Const.RSP_IDG)
        self.tab4_rasp_view.hideColumn(Const.RSP_IDD)
        self.tab4_rasp_view.resizeColumnsToContents()
        self.tab4_rasp_view.setCurrentIndex(self.tab4_rasp_view.model().index(0, 0))
        self.tab4_rasp_view.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.tab4_journ_view.setModel(JournQTableModel(self.journ))
        self.rasp_curent_row = -1
        self.tab4_rasp_view.installEventFilter(self)
        #        self.tab4_journ_view.installEventFilter(self)

        self.tab4_add_journ.clicked.connect(self.journ_corrector)
        self.tab4_del_journ.clicked.connect(self.journ_corrector)
        self.tab4_journ_view.doubleClicked.connect(self.edit_journ_record)

        self.installEventFilter(self)

    def edit_journ_record(self):
        print('edit')

    def journ_corrector(self):
        object = self.sender().objectName()
        if object == 'tab4_del_journ':
            del_cnt = 0
            id_select = []
            for index in self.tab4_journ_view.selectedIndexes():
                if index.column() == 0:
                    if len(self.journ.cache[index.row()][Const.JRN_THEME].strip()) < 9:
                        id = self.journ.cache[index.row()][Const.JRN_ID]
                        self.journ.rec_delete(id)
                        del_cnt += 1
                    else:
                        self.message_out.emit(
                            f"Невозможно удалить запись журнала: "
                            f"'{self.journ.cache[index.row()][Const.JRN_THEME].strip()}'")
            if del_cnt:
                self.journ_update()
        elif object == 'tab4_add_journ':
            if self.tab4_lmonts.currentText():
                month = int(self.tab4_lmonts.currentText().split()[0])

                list_days = dict()
                if self.rasp.rows() > 0:
                    for item in self.rasp.cache:
                        if item[self.IDGROUPS_POS] == self.idGroups:
                            list_days[item[self.IDDAY_POS]] = [item[self.START_POS], item[self.END_POS]]
                    list_days = qget_days_list(list_days, month)
                    test = [] if self.journ.rows() == 0 else [day[1] for day in self.journ.cache]
                    for rec in list_days:
                        if rec[0] not in test:
                            arg = dict()
                            arg['idGroups'] = str(self.idGroups)
                            arg['date'] = rec[0]
                            arg['name'] = 'Тема...'
                            arg['tstart'] = rec[1]
                            arg['tend'] = rec[2]
                            self.journ.rec_append(arg)
                    self.journ_update()

    def journ_update(self):
        self.journ.refresh_select()
        self.tab4_journ_view.setModel(JournQTableModel(self.journ))
        self.tab4_journ_view.hideColumn(Const.JRN_ID)
        self.tab4_journ_view.hideColumn(Const.JRN_ESTIM)
        self.tab4_journ_view.hideColumn(Const.JRN_SHTRAF)
        self.tab4_journ_view.hideColumn(Const.JRN_USRCOMM)
        self.tab4_journ_view.hideColumn(Const.JRN_IDG)
        self.tab4_journ_view.resizeColumnsToContents()
        self.tab4_journ_view.setCurrentIndex(self.tab4_rasp_view.model().index(0, 0))
        self.tab4_journ_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tab4_count_journ.display(self.journ.rows())
        self.tab4_journ_view.update()

    def restate_commit(self):
        if Const.IN_TRANSACTION:
            Const().to_commit(self.con)
            self.tab4_commit_frame.show()
            self.tab4_commit_btn.setDisabled(False)
            self.tab4_rollback_btn.setDisabled(False)
        else:
            self.tab4_commit_frame.hide()
            self.tab4_commit_btn.setDisabled(True)
            self.tab4_rollback_btn.setDisabled(True)

    def eventFilter(self, object: 'QObject', event: 'QEvent') -> bool:
        if self.tab4_rasp_view.isEnabled():
            if Const.IN_TRANSACTION:
                Const().to_commit(self.con)
                self.tab4_commit_frame.show()
                self.tab4_commit_btn.setDisabled(False)
                self.tab4_rollback_btn.setDisabled(False)
            else:
                self.tab4_commit_frame.hide()
                self.tab4_commit_btn.setDisabled(True)
                self.tab4_rollback_btn.setDisabled(True)
            self.restate_commit()
            if object.objectName() == 'tab4_journ_view':
                if event.type() == QEvent.MouseButtonDblClick:
                    if Const.TEST_MODE:
                        print('dbl')
            elif object.objectName() == 'tab4_rasp_view':
                row = object.currentIndex().row()
                col = 1
                if row != self.rasp_curent_row:
                    self.rasp_curent_row = row
                    self.change_current_journ()
        else:
            if event.type() == QEvent.KeyPress:
                if event.key() == QtCore.Qt.Key_Escape:
                    if Const.TEST_MODE:
                        print('esc')
                    self.clicked_cancel.emit()
                elif event.key() == QtCore.Qt.Key_Return:
                    if Const.TEST_MODE:
                        print('enter')
                    self.clicked_enter.emit()
                elif event.key() == QtCore.Qt.Key_F2:
                    if Const.IN_TRANSACTION:
                        Const().to_commit(self.con)
                        self.tab4_commit_btn.click()
        # -----------------------
        return False

    def change_current_journ(self):
        #        self.tab4_journ_view.model().beginResetModel()
        #        print(self.tab4_rasp_view.model().rowCount())
        try:
            self.id = self.rasp.cache[self.tab4_rasp_view.currentIndex().row()][0]
            self.idGroups = self.rasp.cache[self.tab4_rasp_view.currentIndex().row()][self.IDGROUPS_POS]
            ngrp = self.rasp.cache[self.tab4_rasp_view.currentIndex().row()][1].split()[0]
        except IndexError:
            self.id = -1
            self.idGroups = -1
            ngrp = ''
        self.tab4_curr_grp.setText(ngrp)
        self.journ.set_param_str((self.idGroups, ))
        self.journ_update()

    def rasp_set_filter(self):
        """
        Подготовка комбобоксов для фильтров
        :return:
        """
        filters = []
        if self.flt_user.count():
            if self.flt_user.currentIndex() > 0:
                id = self.flt_user.currentText().split()[0]
                filters.append(f'g.idUsers = {id}')
            if self.flt_day.currentIndex() > 0:
                id = self.flt_day.currentIndex() - 1
                filters.append(f'r.idDays = {id}')
            if self.flt_kab.currentIndex() > 0:
                id = self.flt_kab.currentIndex() - 1
                filters.append(f'r.idKabs = {id}')
            #            self.tab4_rasp_view.model().beginResetModel()
            if filters:
                self.rasp.prepare_str_modify(f""" and {' and '.join(filters)}""")
            else:
                self.rasp.prepare_str_modify()
            self.rasp.refresh_select()
            #            self.tab4_rasp_view.model().endResetModel()
            self.activate()

    def group_clicked(self):
        """
        Обработка кнопок редактора расписания
        :return:
        """
        btn = self.sender()
        name_btn = btn.objectName()
        if 'commit' in name_btn:
            self.rasp.commit_table()
            self.map_table()
            return
        elif 'rollback' in name_btn:
            self.rasp.rollback_table()
            self.map_table()
            return
        elif 'del' in name_btn:
            for row in [id.row() for id in self.tab4_rasp_view.selectedIndexes() if id.column() == 0]:
                id = self.rasp.cache[row][0]
                self.rasp.rec_delete(id)
            self.map_table()
            return
        elif 'add' in name_btn:
            self.id = 0
        elif 'edit' in name_btn:
            self.id = self.rasp.cache[self.tab4_rasp_view.currentIndex().row()][0]
        self.start_edit_rasp()

    def start_edit_rasp(self):
        """
        Начало работы режима редактора расписания
        :return:
        """
        self.current_data = []
        self.create_edit_widgets()
        self.tab4_rasp_view.setDisabled(True)
        for btn in self.tab4_btn_group.buttons():
            btn.setDisabled(True)
        self.tab4_filter_frame.setEnabled(False)
        self.tab4_journ_frame.setEnabled(False)

    def showEvent(self, a0):
        self.activate()
        # self.map_table()
        return super().showEvent(a0)

    def map_table(self):
        """
        Обновление формы расписания и цветовых маркеров
        :return:
        """
        self.tab4_rasp_view.setDisabled(False)
        for btn in self.tab4_btn_group.buttons():
            btn.setDisabled(False)
        self.tab4_filter_frame.setEnabled(True)
        self.tab4_journ_frame.setEnabled(True)

        self.rasp.refresh_select()
        self.tab4_count_lcd.display(self.rasp.rows())
        self.tab4_rasp_view.setModel(RaspQTableModel(self.rasp))
        self.tab4_rasp_view.hideColumn(Const.RSP_ID)
        self.tab4_rasp_view.hideColumn(Const.RSP_CNTLESS)
        self.tab4_rasp_view.hideColumn(Const.RSP_IDG)
        self.tab4_rasp_view.hideColumn(Const.RSP_IDD)
        self.tab4_rasp_view.resizeColumnsToContents()
        self.tab4_rasp_view.setCurrentIndex(self.tab4_rasp_view.model().index(0, 0))
        self.tab4_rasp_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        for d, day in enumerate(self.days_lst):
            for k, kab in enumerate(self.kab_lst):
                for t, time in enumerate(self.time_lst):
                    widg: QLabelClk = self.slots_dic.get(f"{d} {k} {t}", None)
                    if widg:
                        widg.setText(self.LABEL_FREE)
                        widg.setStyleSheet(
                            f"""background-color: rgb(255, 255, 255); font: {self.FONT_SIZE}pt "MS Shell Dlg 2";""")
        if not self.rasp.rows():
            return
        for rec in self.rasp.cache:
            nday = self.days_lst.index(rec[2])
            nkab = -1
            for i, val in enumerate(self.kab_lst):
                if val[0] == rec[3]:
                    nkab = i
            for i, t in enumerate(self.time_lst):
                if rec[4] <= t < rec[5]:
                    widg: QLabel = self.slots_dic.get(f"{nday} {nkab} {i}", None)
                    if widg:
                        if widg.text() == self.LABEL_OK:
                            self.collisium.emit()
                            widg.setText(self.LABEL_COLL)
                        else:
                            widg.setText(self.LABEL_OK)
                            widg.setToolTip(f"{rec[0]} {rec[1]}")

                        widg.setStyleSheet(
                            f"""background-color: rgb{self.kab_lst[nkab][1]}; font: {self.FONT_SIZE}pt "MS Shell Dlg 2";""")
        self.tab4_rasp_view.setFocus()

    def set_current_record(self, id=None):
        """
        Перенос текущего указателя списка расписания
        :param id: УН записи расписания
        :return:
        """
        for i in range(self.tab4_rasp_view.model().rowCount()):
            if self.tab4_rasp_view.model().itemData(self.tab4_rasp_view.model().index(i, 0))[0] == id:
                self.tab4_rasp_view.setCurrentIndex(self.tab4_rasp_view.model().index(i, 0))
                self.tab4_rasp_view.update()

    def color_table_click(self):
        """
        Обработка клика мыши в цветовом поле
        :return:
        """
        if len(self.edit_widgets):
            return
        lbl = self.sender()
        #        print(lbl.objectName())
        if lbl.toolTip():
            self.set_current_record(lbl.toolTip().split()[0])
            self.tab4_rasp_view.setFocus()

    def color_table_dbl_click(self):
        """
        Обработка двойного клика мыши в цветовом поле
        :return:
        """
        if len(self.edit_widgets):
            return
        lbl = self.sender()
        #        print(lbl.toolTip())
        if lbl.toolTip():
            self.set_current_record(lbl.toolTip().split()[0])
            self.tab4_edit_btn.click()
        else:
            day, kab, tim = lbl.objectName().split()
            self.new_preset.clear()
            self.new_preset['idDays'] = int(day)
            self.new_preset['idKabs'] = int(kab)
            self.new_preset['tstart'] = self.time_lst[int(tim)]
            self.new_preset['tend'] = self.add1_5hours(self.time_lst[int(tim)])

            self.tab4_add_btn.click()
        # print('dbl', lbl.objectName())

    def add1_5hours(self, time0: str):
        """
        Увеличение временной метки на 1,5 часа
        :param time0: метка времени '08:30'
        :return: '10:00'
        """
        try:
            h, m = time0.split(':')
            m2 = (int(m) + 30) % 60
            h2 = int(h) + 1 + (int(m) + 30) // 60
        except Exception:
            m2 = 0
            h2 = 0
        return (f"{h2:02}:{m2:02}")

    def create_day(self, day=0):
        """
        Создание визуальной формы на конкретный день
        :param day: Номер дня
        :return: заполненный Layout
        """
        MAX_F = 20
        MAX_T = 35
        obj = QGridLayout()
        obj.setAlignment(QtCore.Qt.AlignCenter)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        head = QLabel(self.short_days_lst[day] + ' ')
        head.setAlignment(QtCore.Qt.AlignLeft)
        head.setStyleSheet(f"""font: {self.FONT_SIZE + 2}pt "MS Shell Dlg 2";""")
        head.setMinimumWidth(MAX_T)
        head.setMaximumWidth(MAX_T)
        head.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        obj.addWidget(head, 0, 0)
        obj.setAlignment(QtCore.Qt.AlignLeft)
        for i, num in enumerate(self.kab_lst):
            lbl = QLabel(f" {num[0]} ")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            lbl.setSizePolicy(sizePolicy)
            lbl.setStyleSheet(f"""font: {self.FONT_SIZE}pt "MS Shell Dlg 2";""")
            lbl.setMaximumWidth(MAX_F)
            obj.addWidget(lbl, 0, i + 1)
        for i in range(len(self.time_lst)):
            lbl = QLabel(f"{self.time_lst[i]}")
            lbl.setMinimumWidth(MAX_T)
            lbl.setMaximumWidth(MAX_T)
            lbl.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
            lbl.setStyleSheet(f"""font: {self.FONT_SIZE}pt "MS Shell Dlg 2";""")
            lbl.setAlignment(QtCore.Qt.AlignLeft)
            obj.addWidget(lbl, i + 1, 0)
            for j, num in enumerate(self.kab_lst):
                ch_b = QLabelClk('')
                ch_b.setText('')
                ch_b.setMaximumWidth(MAX_F)
                ch_b.clicked.connect(self.color_table_click)
                ch_b.dblClicked.connect(self.color_table_dbl_click)
                ch_b.setAlignment(QtCore.Qt.AlignCenter)
                ch_b.setObjectName(f"{day} {j} {i}")
                ch_b.setStyleSheet(
                    f"""background-color: rgb(255, 255, 255);  font: {self.FONT_SIZE}pt "MS Shell Dlg 2";""")
                sizePolicy.setHeightForWidth(ch_b.sizePolicy().hasHeightForWidth())
                ch_b.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
                self.slots_dic[ch_b.objectName()] = ch_b
                obj.addWidget(ch_b, i + 1, j + 1)
        v_line = QFrame()
        v_line.setFrameShape(QFrame.VLine)
        obj.addWidget(v_line, 0, len(self.kab_lst) + 1, len(self.time_lst) + 2, len(self.kab_lst) + 1)
        return obj

    def delete_edit_form(self, curLayout):
        """ Удаляем поля редактирования
        """
        for widg in self.edit_widgets:
            curLayout.removeWidget(widg)
            widg.deleteLater()
        self.edit_widgets.clear()

    def create_edit_widgets(self):
        """
        Создаём поля для ввода данных по расписанию
        :return:
        """
        curLayout = self.tab4_edit_layout
        """ Создание полей редактирования записи """
        self.current_data = self.rasp.get_record(self.id)
        print(self.current_data)
        self.delete_edit_form(curLayout)
        if not self.current_data[0][2] and self.new_preset:
            self.current_data[1][2] = self.new_preset['idDays']
            self.current_data[2][2] = self.new_preset['idKabs']
            self.current_data[3][2] = self.new_preset['tstart']
            self.current_data[4][2] = self.new_preset['tend']
            self.new_preset.clear()
        lrow = 0
        sP = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        lP = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        for i, val in enumerate(self.current_data):
            self.edit_widgets.append(QLabel(val[1], self))
            curLayout.addWidget(self.edit_widgets[-1], i, 0)
            self.edit_widgets[-1].setSizePolicy(lP)
            if val[0] == 'id':
                pass
            elif val[0][:2] == 'id':
                self.edit_widgets.append(QComboBox(self))
                self.edit_widgets[-1].setDisabled(False)
                self.edit_widgets[-1].setSizePolicy(sP)
                self.edit_widgets[-1].setFocusPolicy(Qt.StrongFocus)
                curLayout.addWidget(self.edit_widgets[-1], i, 1)
                sql = f"""select id, trim(name) as name from {val[0][2:]} order by name"""
                spis = self.rasp.execute_command(sql)
                spis = [f"{v[0]:4} : {v[1]}" for v in spis]
                idx = -1
                for i, el in enumerate(spis):
                    self.edit_widgets[-1].addItem(el)
                    if int(el.split()[0]) == val[2]:
                        idx = i
                self.edit_widgets[-1].setCurrentIndex(idx)
            else:
                le = QLineEdit(str(val[2]), self)
                if val[0][:] in ['tstart', 'tend']:
                    le.setInputMask('99:99')
                    le.setObjectName(val[0][:])
                    if val[0][:] == 'tend':
                        le.returnPressed.connect(self.calculate)
                    else:
                        le.returnPressed.connect(self.selected_edit)
                self.edit_widgets.append(le)
                curLayout.addWidget(self.edit_widgets[-1], i, 1)
                self.edit_widgets[-1].setSizePolicy(sP)
            self.edit_widgets[1].setFocus()
            lrow = i
        pbS = QPushButton('Применить')
        pbS.setSizePolicy(sP)
        pbS.setObjectName('Save')
        pbS.clicked.connect(self.edit_buttons)
        self.clicked_enter.connect(pbS.click)
        curLayout.addWidget(pbS, 4, 2)
        self.edit_widgets.append(pbS)
        pbC = QPushButton('Отменить')
        pbC.setSizePolicy(sP)
        pbC.setObjectName('Cancel')
        pbC.clicked.connect(self.edit_buttons)
        self.clicked_cancel.connect(pbC.click)
        curLayout.addWidget(pbC, 5, 2)
        curLayout.addWidget(QFrame(), 0, 3, lrow, 3)
        self.edit_widgets.append(pbC)

    def calculate(self, object):
        """
        Вычисляем +1,5 часа к записи 'tstart'
        :param object: Куба положить результат
        :return:
        """
        new = ''
        for key, _, val in self.current_data:
            if key == 'tstart':
                new = self.add1_5hours(val)
                break
        object.setText(new)

    def selected_edit(self):
        """
        Выделение поля ввода виджета sender()
        :return:
        """
        if self.sender().objectName() in ['tstart', 'tend']:
            self.sender().selectAll()

    def edit_buttons(self):
        """
        Завершаем редактироваие/ввод записи расписания
        :return:
        """
        if self.sender().objectName() in 'Save':
            self.update_edit_frame()
        self.delete_edit_form(self.tab4_edit_layout)
        self.map_table()

    def update_edit_frame(self):
        """
        Сохраняем результаты редактирования. либо создание новой записи
        :return:
        """
        arg = {}
        for i, widg in enumerate(self.edit_widgets[1:-2:2]):
            if type(widg) == QLineEdit:
                arg[self.current_data[i][0]] = widg.text().strip()
            elif type(widg) == QComboBox:
                fnd = widg.currentText()
                id = fnd[:fnd.find(':') - 1]
                arg[self.current_data[i][0]] = str(id)
            else:
                print('Ошибочный тип в редакторе!')
        for widg in self.edit_widgets:
            widg.deleteLater()
        self.edit_widgets.clear()
        if self.id == 0:
            self.rasp.rec_append(arg)
        else:
            self.rasp.rec_update(self.id, arg)

    def activate(self):
        """ Проверка на сохранение данных при выходе из программы

        """
        self.delete_edit_form(self.tab4_edit_layout)
        self.map_table()
        self.change_current_journ()
        # self.show()

    # def eventFilter(self, object: 'QObject', event: 'QEvent') -> bool:
    """ 
    Обрабатываем события формы
    """
    #     # # print(object.objectName(), event.type())
    #     # if object.objectName() == 'tend':
    #     #     if event.type() == 12:
    #     #         self.calculate(object)
    #     return super().eventFilter(object, event)


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    flog = LogWriter()

    spl = QSplashScreen(QPixmap('../Splash/Splash01-02.PNG'))
    spl.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
    spl.show()
    if QtConnectDb('../settings.ini').get_con():
        if Const.TEST_MODE:
            print('Connect: Ok')
        qsql = QSqlQuery()
        qsql.exec(f"select id from users where winlogin = '{os.getlogin()}'")
        qsql.first()
        wnd = QTab4FormWindow(15)
        spl.finish(wnd)
        wnd.show()
    sys.exit(app.exec())
