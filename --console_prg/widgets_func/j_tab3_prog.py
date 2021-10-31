import sys
import sqlite3

from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QWidget, QApplication, QAbstractItemView

from classes.cl_const import Const
from classes.cl_courses import Courses
from classes.cl_group_table import GroupTable
from classes.cl_groups import Groups
from classes.cl_users import Users
from forms_journ.t_tab3 import Ui_tab3Form


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class Tab3FormWindow(QWidget, Ui_tab3Form):
    def __init__(self, con):
        super(Tab3FormWindow, self).__init__()
        self.setupUi(self)
        self.initUi(con)

    def initUi(self, con):
        self.con = con  # connector to SQL

        self.crs = Courses(con)
        self.grp = Groups(con)
        self.grp_tbl = GroupTable(con)
        self.usrs = Users(con, date_col=7)

        self.tab3_program_box.addItems([f"{item[0]:3}: {item[6]:5} :{item[2]:<8} : {item[1]}"
                                        for item in self.crs.data])
        self.tab3_program_box.setCurrentIndex(2)
        self.tab3_programm_lcd.display(len(self.crs.data))
        self.tab3_change_program()
        self.tab3_change_users()

        self.tab3_only_free.stateChanged.connect(self.tab3_change_users)
        self.tab3_program_box.currentTextChanged.connect(self.tab3_change_program)  # Смена уч.программы

        self.tab3_group_list.clicked.connect(self.tab3_change_group)  # Смена учебной группы
        self.tab3_add_button.clicked.connect(self.tab3_add_to_group)
        self.tab3_del_button.clicked.connect(self.tab3_erase_from_group)
        self.tab3_commit_button.hide()
        self.tab3_cancel_button.hide()
        self.tab3_commit_button.clicked.connect(self.tab3_commit_base)
        self.tab3_cancel_button.clicked.connect(self.tab3_rollback_base)

    # def tab3_current_display(self, cur, prev):
    #     print(cur, prev)
    #     # self.tab3_users_current.setText(self.usrs.data[self.tab3_users_table.currentIndex().row()][2])

    def tab3_change_users(self):
        sql = ''
        if self.tab3_only_free.isChecked():
            sql = f"""select distinct u.id as 'ID', u.name as 'Фамилия И.О.', u.sertificate as 'серт.ПФДО',
                   p.name as 'Место учёбы/работы', p.comment as 'Класс/Должн.', 
                   u.phone as 'Телефон', u.birthday as 'Д.рожд',  
                   u.comment as 'Доп.информация'
                    from users u
                    join places p on u.idPlaces = p.id
                    left join group_table g on g.idUsers = u.id
                  where idRoles = 2 and g.id is NULL"""
        else:
            sql = f"""select distinct u.id as 'ID', 
                   (select count(*) from group_table gt where gt.idUsers = u.id) as '!', 
                   u.name as 'Фамилия И.О.', u.sertificate as 'серт.ПФДО',
                   p.name as 'Место учёбы/работы', p.comment as 'Класс/Должн.', 
                   u.phone as 'Телефон', u.birthday as 'Д.рожд',  
                   u.comment as 'Доп.информация'
                    from users u
                    join places p on u.idPlaces = p.id
                    left join group_table g on g.idUsers = u.id
                  where idRoles = 2 """
        self.usrs.set_sql(sql, 'u.id')
        self.usrs.update()
        self.tab3_users_table.setModel(self.usrs.model())
        self.tab3_users_table.resizeColumnsToContents()
        self.tab3_users_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tab3_reserv_lcd.display(len(self.usrs.data))

    def tab3_change_group(self):
        idGroups = self.grp.data[self.tab3_group_list.currentIndex().row()][0]
        sql = f"""select t.id as 'id', u.name as 'Фамилия И.О.', u.sertificate as 'серт.ПФДО',
                    t.comment as 'Комментарий', p.comment as 'Класс',
                    p.name as 'Уч.заведение'
                from group_table t
                join users u on u.id = t.idUsers
                join places p on p.id = u.idPlaces
                where t.idGroups = {idGroups}"""
        self.grp_tbl.set_sql(sql, 'u.name')
        self.grp_tbl.update()
        self.tab3_sostav_table.setModel(self.grp_tbl.model())
        self.tab3_sostav_table.resizeColumnsToContents()
        self.tab3_sostav_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tab3_counter_lcd.display(self.grp_tbl.rows())
        self.tab3_sostav_table.selectRow(0)
        sql = f"""select count(*) from group_table group by idUsers"""
        cnt = self.grp_tbl.execute_command(sql)
        if cnt:
            self.tab3_volume_lcd.display(cnt[0][0])
        else:
            self.tab3_volume_lcd.display(0)
        sql = f"""select sum(c.lesson) * 2 from courses c
                left join groups g on g.idCourses = c.id
                left join group_table gt on gt.idGroups = g.id"""
        cnt = self.grp_tbl.execute_command(sql)
        if cnt:
            self.tab3_ned_lcd.display(cnt[0][0])
        else:
            self.tab3_ned_lcd.display(0)

    def tab3_change_program(self):
        tst  = self.tab3_program_box.currentText()
        idCourses = int(tst[:tst.find(':')])
        sql = f"""select g.id, g.name as 'Группа', c.year as 'Уч.год', u.name as 'ФИО наставника',
                (select count(*) from group_table gt where gt.idGroups = g.id) as 'Кол-во детей'
                from groups g
                join users u on g.idUsers = u.id
                join courses c on g.idCourses = c.id
              where g.idCourses = {idCourses}"""
        self.grp.set_sql(sql, 'g.name')
        self.grp.update()
        self.tab3_group_list.setModel(self.grp.model())
        for i in range(len(self.grp.data[0])):
            self.tab3_group_list.resizeColumnToContents(i)  #  resizeColumnsToContents()
        self.tab3_group_list.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tab3_group_list.setRootIndex(QModelIndex())  # selectRow(0)
        sql = f"""select count(*) from groups"""
        cnt = self.grp.execute_command(sql)
        if cnt:
            self.tab3_groups_lcd.display(cnt[0][0])
        else:
            self.tab3_groups_lcd.display(0)
        self.tab3_change_group()

    def tab3_check_for_commit(self):
        """
        Диалог для COMMIT - ROLLBACK изменений
        """
        if Const.IN_TRANSACTION:
            Const().to_commit(self.con)
            self.tab3_commit_button.setDisabled(False)
            self.tab3_cancel_button.setDisabled(False)
        else:
            self.tab3_commit_button.setDisabled(True)
            self.tab3_cancel_button.setDisabled(True)

    def tab3_add_to_group(self):
        idGroups = self.grp.data[self.tab3_group_list.currentIndex().row()][0]
        for index in [id.row() for id in self.tab3_users_table.selectedIndexes() if id.column() == 0]:
            idUsers = self.usrs.data[index][0]
            self.grp_tbl.rec_append({'idGroups': str(idGroups), 'idUsers' : str(idUsers)})
        self.tab3_refresh_all()

    def tab3_erase_from_group(self):
        for index in [id.row() for id in self.tab3_sostav_table.selectedIndexes() if id.column() == 0]:
            id = self.grp_tbl.data[index][0]
            self.grp_tbl.rec_delete(id)
        self.tab3_refresh_all()

    def tab3_commit_base(self):
        self.usrs.commit()
        self.tab3_refresh_all()

    def tab3_rollback_base(self):
        self.usrs.rollback()
        self.tab3_refresh_all()

    def tab3_refresh_all(self):
        self.tab3_change_program()
        self.tab3_change_users()
        self.tab3_check_for_commit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys.excepthook = except_hook
    con = sqlite3.connect('..\\db\\database_J.db')
    wnd = Tab3FormWindow(con)
    wnd.show()
    sys.exit(app.exec())