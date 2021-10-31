from PyQt5.QtWidgets import QLabel, QMainWindow, QAbstractItemView, QMessageBox, QLineEdit, \
    QComboBox, QDialogButtonBox, QHBoxLayout
from PyQt5 import QtGui
from PyQt5.QtCore import Qt

from classes.cl_logwriter import LogWriter
from classes.cl_users import Users
from classes.db__classes import Privileges, Roles, Places, Courses, Groups
from classes.bb_converts import *
from forms_journ.t_tab1_2 import Ui_MainWindow

from widgets_func.j_tab4_prog import Tab4FormWindow
from widgets_func.j_tab3_prog import Tab3FormWindow
from widgets_func.j_tab5_prog import T5Window
from widgets_func.j_tab6_prog import T6Window
from classes.cl_const import Const


class MWindow(QMainWindow, Ui_MainWindow):  # Главное окно приложения
    def __init__(self, con, login_id):
        super(MWindow, self).__init__()
        self.setupUi(self)
        # uic.loadUi('widgets_journal\\t_tab1_2.ui', self)
        self.initUi(con, login_id)

    def initUi(self, con, login_id):
        """
        Начальная настройка форм первых двух вкладок
        :param con:
        :return:
        """
        self.logfile = LogWriter()
        self.setWindowTitle('IT-куб. Белая Холуница. Журналы. v.1.0')
        self.con = con
        self.login_id = login_id
        self.id = None
        self.currTable = None
        self.edit_widgets = []
        self.table_list = {
            0: ('Привилегии доступа', Privileges(self.con)),
            1: ('Роли пользователей', Roles(self.con)),
            2: ('Места работы/учёбы', Places(self.con)),
            3: ('Учебные программы', Courses(self.con)),
            4: ('Учебные группы', Groups(self.con))
        }
        self.listBox.addItems([val[0] for val in self.table_list.values()])
        self.listBox.currentIndexChanged.connect(self.tab1_change_table)
        self.listBox.setCurrentIndex(3)

        self.tab3_myLayout = QHBoxLayout(self)
        self.tab3.setLayout(self.tab3_myLayout)
        self.tab3_myLayout.addWidget(Tab3FormWindow(con))

        self.tab4_myLayout = QHBoxLayout(self)
        self.tab4.setLayout(self.tab4_myLayout)
        self.tab4_myLayout.setContentsMargins(0, 0, 0, 0)
        self.tab4Widget = Tab4FormWindow(con, self.login_id)
        self.tab4_myLayout.addWidget(self.tab4Widget)
        self.tab4Widget.collisium.connect(self.rasp_coll)

        self.tab5_myLayout = QHBoxLayout(self)
        self.tab5.setLayout(self.tab5_myLayout)
        self.tab5_myLayout.setContentsMargins(0, 0, 0, 0)
        self.tab5Widget = T5Window(con, self.login_id)
        self.tab5_myLayout.addWidget(self.tab5Widget)

        self.tab6_myLayout = QHBoxLayout(self)
        self.tab6.setLayout(self.tab6_myLayout)
        self.tab6_myLayout.setContentsMargins(0, 0, 0, 0)
        self.tab6Widget = T6Window(con, self.login_id)
        self.tab6_myLayout.addWidget(self.tab6Widget)

        self.tableView.doubleClicked.connect(self.edit_Button.click)
        self.MainTab.currentChanged.connect(self.main_prepare_tab)
        self.buttonEditFrame.button(QDialogButtonBox.Save).setText('Сохранить')
        self.buttonEditFrame.button(QDialogButtonBox.No).setText('Отмена')
        self.fltCheck.stateChanged.connect(self.tab1_filter)
        self.add_Button.clicked.connect(self.tab1_clicked_buttons)
        self.edit_Button.clicked.connect(self.tab1_clicked_buttons)
        self.del_Button.clicked.connect(self.tab1_clicked_buttons)
        self.commit_Button.clicked.connect(self.tab1_clicked_buttons)
        self.rollback_Button.clicked.connect(self.tab1_clicked_buttons)
        self.buttonEditFrame.rejected.connect(self.tab1_deactivateEditFrame)
        self.buttonEditFrame.accepted.connect(self.tab1_save_edit_frame)
        self.MainTab.tabBarClicked.connect(self.check_for_commit)
        self.tab2_buttonBox.button(QDialogButtonBox.Save).setText('Сохранить')
        self.tab2_buttonBox.button(QDialogButtonBox.Cancel).setText('Отмена')
        self.currTable.need_to_save.connect(self.tab2_refresh_form)
        self.tableView_Users.doubleClicked.connect(self.tab2_edit_form)
        self.tab2_del.clicked.connect(self.tab2_clicked_buttons)
        self.tab2_add.clicked.connect(self.tab2_clicked_buttons)
        self.tab2_edit.clicked.connect(self.tab2_clicked_buttons)
        self.tab2_commit.clicked.connect(self.tab2_clicked_buttons)
        self.tab2_rollback.clicked.connect(self.tab2_clicked_buttons)
        self.tab2_buttonBox.rejected.connect(self.tab2_deactivateEditFrame)
        self.tab2_buttonBox.accepted.connect(self.tab2_save_edit_frame)
        self.MainTab.setCurrentIndex(4)
        self.tab5Widget.activate()
        # self.tab2_activate()

    def rasp_coll(self):
        self.statusbar.showMessage('Коллизия расписания!!!', 1000)

    def main_prepare_tab(self):
        """
        Переключение окон главного окна
        """
        if self.tab1.isVisible():
            self.tab1_activate()
        elif self.tab2.isVisible():
            self.tab2_activate()
        elif self.tab3.isVisible():
            pass
            # print('tab3')
            # self.tab3.show()
        elif self.tab4.isVisible():
            self.tab4Widget.activate()
        elif self.tab5.isVisible():
            self.tab5Widget.activate()
            # print('tab5')
        elif self.tab6.isVisible():
            print('tab6')

    def create_edit_widgets(self, curLayout):
        """
        Создание полей редактирования записи
        """
        self.current_data = self.currTable.get_record(self.id)
        self.delete_edit_form(curLayout)
        for i, val in enumerate(self.current_data):
            self.edit_widgets.append(QLabel(val[1], self))
            curLayout.addWidget(self.edit_widgets[-1], i + 2, 0)
            if val[0][:2] == 'id':
                self.edit_widgets.append(QComboBox(self))
                c = QComboBox()
                self.edit_widgets[-1].setFocusPolicy(Qt.StrongFocus)
                curLayout.addWidget(self.edit_widgets[-1], i + 2, 1)
                if val[0][2:] == 'Users':
                    spis = Users(self.con).priv_users()
                else:
                    sql = f"""select id, trim(name), trim(comment) from {val[0][2:]}"""
                    spis = self.currTable.execute_command(sql)
                # spis = [f"{val[0]:4} : {val[1]} : {val[2]}" for val in spis]
                idx = -1
                for i, spr in enumerate(spis):
                    self.edit_widgets[-1].addItem(f"{spr[0]:4} : {spr[1]} : {spr[2]}")
                    if spr[0] == val[2]:
                        idx = i
                self.edit_widgets[-1].setCurrentIndex(idx)
            else:
                if val[0] == 'birthday':
                    val[2] = date_us_ru(val[2])
                self.edit_widgets.append(QLineEdit(str(val[2]).strip(), self))
                curLayout.addWidget(self.edit_widgets[-1], i + 2, 1)
            self.edit_widgets[1].setFocus()

    def update_edit_frame(self):
        """
        Сохраняем результаты редактирования. либо создание новой записи
        """
        arg = {}
        for i, widg in enumerate(self.edit_widgets[1::2]):
            if type(widg) == QLineEdit:
                if self.current_data[i][0] == 'birthday':
                    arg[self.current_data[i][0]] = date_ru_us(widg.text())
                else:
                    arg[self.current_data[i][0]] = widg.text().replace(':', '-')
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
            self.currTable.rec_append(arg)
        else:
            self.currTable.rec_update(self.id, arg)

    def delete_edit_form(self, curLayout):
        """
        Удаляем поля редактирования
        """
        for widg in self.edit_widgets:
            curLayout.removeWidget(widg)
            widg.deleteLater()
        self.edit_widgets.clear()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        """
        Проверка на сохранение данных при выходе из программы
        """
        self.check_for_commit()
        self.logfile.to_log(f"""Завершение работы. [{self.login_id}]""")
        return QMainWindow.closeEvent(self, a0)

    def check_for_commit(self):
        """
        Диалог для COMMIT - ROLLBACK изменений
        """
        if Const.IN_TRANSACTION:
            buttonReply = QMessageBox.question(self, 'Редактор', "Остались несохранённые изменения, сохранить?",
                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if buttonReply == QMessageBox.Yes:
                self.currTable.commit()
            else:
                self.currTable.rollback()

    def tab1_clicked_buttons(self):
        """
        Обработка нажатий правого поля кнопок на ТАБ 1
        """
        obj_name = self.sender().objectName()
        if obj_name == 'del_Button':
            self.currTable.rec_delete(self.currTable.data[self.tableView.currentIndex().row()][0])
            self.tab1_refresh_table()
            return
        elif obj_name == 'commit_Button':
            self.currTable.commit()
            self.tab1_refresh_table()
            return
        elif obj_name == 'rollback_Button':
            self.currTable.rollback()
            self.tab1_refresh_table()
            return
        elif obj_name == 'edit_Button':
            self.id = self.currTable.data[self.tableView.currentIndex().row()][0]
        elif obj_name == 'add_Button':
            self.id = 0
            self.current_data = []
        self.create_edit_widgets(self.gridLayout)
        self.editFrame.show()
        for button in self.buttonMainGroup.buttons():
            button.setDisabled(True)
        self.listBox.setDisabled(True)
        self.tableView.setDisabled(True)

    def tab1_refresh_table(self):
        """
        Смена текушей таблицы. Обновление формы
        """
        self.currTable.update()
        self.tableLabel.setText(f"{self.listBox.currentText()}   ({len(self.currTable.data)})")
        self.tableView.setModel(self.currTable.model())
        self.tableView.resizeColumnsToContents()
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.setDisabled(False)

        if Const.IN_TRANSACTION:
            Const().to_commit(self.con)
            self.transLabel.setText('')
            self.commit_Button.setFlat(False)
            self.rollback_Button.setFlat(False)
            self.commit_Button.setDisabled(False)
            self.rollback_Button.setDisabled(False)
        else:
            self.transLabel.setText('')
            self.commit_Button.setFlat(True)
            self.rollback_Button.setFlat(True)
            self.commit_Button.setDisabled(True)
            self.rollback_Button.setDisabled(True)
        if len(self.currTable.data[0]) == 0:
            self.del_Button.setDisabled(True)
            self.edit_Button.setDisabled(True)
        else:
            self.del_Button.setDisabled(False)
            self.edit_Button.setDisabled(False)

    def tab1_filter(self):
        """
        Работа с фильтром данных
        """
        if self.fltCheck.isChecked():
            # fio = list(filter(lambda x: x[0] == 'idUsers', self.currTable.keys))
            # print(fio)
            fio = self.currTable.dbname == 'groups'

            if fio:
                sql = f"""select distinct u.id, trim(u.name) from users u
                        join groups g on g.idUsers = u.id"""
                spis = self.currTable.execute_command(sql)
                spis = [f"{v[0]:4} : {v[1]}" for v in spis]
                self.flt_fio.insertItem(0, ' ')
                self.flt_fio.insertItems(1, spis)
                self.flt_fio.setCurrentIndex(0)
                self.flt_fio.currentIndexChanged.connect(self.add_user_filter)
                self.fltLabel1.show()
                self.flt_fio.show()
            # self.fltLabel2.show()
            # self.fltCombo2.show()
            # self.fltLabel3.show()
            # self.fltCombo3.show()
        else:
            self.fltLabel1.hide()
            self.flt_fio.hide()
            self.flt_fio.clear()
            if self.flt_fio.currentIndexChanged == self.add_user_filter:
                self.flt_fio.currentIndexChanged.disconnect()

            self.fltLabel2.hide()
            self.fltCombo2.hide()
            self.fltLabel3.hide()
            self.fltCombo3.hide()

    def add_user_filter(self):
        if self.flt_fio.currentText().strip():
            id = self.flt_fio.currentText().split()[0]
            self.currTable.set_filter(f'g.idUsers = {id}')
        else:
            self.currTable.set_filter()
        self.tab1_refresh_table()

    def tab1_change_table(self):
        """
        Переключаем текущую таблицу
        """
        self.fltCheck.setChecked(False)
        self.tableLabel.setText(self.listBox.currentText())
        self.currTable = self.table_list[self.listBox.currentIndex()][1]
        self.currTable.update()
        self.tab1_refresh_table()
        self.tableView.selectRow(0)

    def tab1_deactivateEditFrame(self):
        self.delete_edit_form(self.gridLayout)
        self.editFrame.hide()
        for button in self.buttonMainGroup.buttons():
            button.setDisabled(False)
        self.listBox.setDisabled(False)
        self.tableView.setDisabled(False)
        self.tab1_refresh_table()

    def tab1_save_edit_frame(self):
        self.update_edit_frame()
        self.tab1_deactivateEditFrame()

    def tab2_refresh_form(self):
        if Const.IN_TRANSACTION:
            Const().to_commit(self.con)
            self.tab2_commit.setFlat(False)
            self.tab2_rollback.setFlat(False)
            self.tab2_commit.setDisabled(False)
            self.tab2_rollback.setDisabled(False)
        else:
            self.tab2_commit.setFlat(True)
            self.tab2_rollback.setFlat(True)
            self.tab2_commit.setDisabled(True)
            self.tab2_rollback.setDisabled(True)
        if len(self.currTable.data[0]) == 0:
            self.tab2_del.setDisabled(True)
            self.tab2_edit.setDisabled(True)
        else:
            self.tab2_del.setDisabled(False)
            self.tab2_edit.setDisabled(False)
        self.currTable.update()
        self.tableView_Users.setModel(self.currTable.model())
        self.tableView_Users.resizeColumnsToContents()
        self.tableView_Users.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.lcdNumber_Users.display(len(self.currTable.data))

    def tab2_edit_form(self):
        if self.tableView_Users.currentIndex().column() not in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            self.tab2_edit.click()

    def tab2_clicked_buttons(self):
        obj_name = self.sender().objectName()
        if obj_name == 'tab2_del':
            self.currTable.rec_delete(self.currTable.data[self.tableView_Users.currentIndex().row()][0])
            self.tab2_refresh_form()
            return
        elif obj_name == 'tab2_commit':
            self.currTable.commit()
            self.tab2_refresh_form()
            return
        elif obj_name == 'tab2_rollback':
            self.currTable.rollback()
            self.tab2_refresh_form()
            return
        elif obj_name == 'tab2_edit':
            self.id = self.currTable.data[self.tableView_Users.currentIndex().row()][0]
        elif obj_name == 'tab2_add':
            self.id = 0
            self.current_data = []
        self.create_edit_widgets(self.gridLayout_2)
        self.tableView_Users.setDisabled(True)
        self.frame_users.show()
        # self.editFrame.show()
        for button in self.tab2_buttonGroup.buttons():
            button.setDisabled(True)

    def tab2_deactivateEditFrame(self):
        self.delete_edit_form(self.gridLayout_2)
        self.frame_users.hide()
        for button in self.tab2_buttonGroup.buttons():
            button.setDisabled(False)
        self.tableView_Users.setDisabled(False)
        self.tab2_refresh_form()

    def tab2_save_edit_frame(self):
        self.update_edit_frame()
        self.tab2_deactivateEditFrame()

    def tab1_activate(self):
        self.delete_edit_form(self.gridLayout)
        self.tab1_change_table()
        self.editFrame.hide()
        self.fltCheck.setChecked(True)
        self.fltCheck.setChecked(False)
        # Фильтр списка

    def tab2_activate(self):
        self.delete_edit_form(self.gridLayout_2)
        self.frame_users.hide()
        self.currTable = Users(self.con, editable=True)
        self.tableView_Users.setModel(self.currTable.model())
        self.tableView_Users.resizeColumnsToContents()
        self.tableView_Users.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tab2_deactivateEditFrame()

