import sqlite3
import sys
from sqlite3 import connect

import pyodbc

from classes.cl_const import Const
from classes.cl_logwriter import LogWriter
from .qt__classes import MyTableModel
from PyQt5.QtCore import pyqtSignal, QObject


class SQLObject(QObject):
    need_to_save = pyqtSignal()

    def __init__(self, con: connect, editable=False, date_col=8):
        """
        Базовый класс работы с БД SQL
        :param con: указатель на БД SQL
        :param editable: Порождать редактируемую модель
        :param date_col:
        """
        super(SQLObject, self).__init__()
        if con is None:
            Exception('NO database connection')
        # self.need_save = pyqtSignal()
        self.logfile = LogWriter()
        self.con : sqlite3.connect = con
        self.cur = con.cursor()
        self.tmodel = None
        self.sql = None
        self.filter = None
        self.order = None
        self.dbname = None
        self.header = []
        self.data = []
        self.keys = []
        self.editable = editable
        self.date_col = date_col
        self.set_filter()
        self.set_order()
        self.set_sql()
        self.update()
        # self.log = Logger(con)

    def rows(self):
        """
        Количество записей в таблице
        :return:
        """
        if len(self.data[0]) == 0:
            return 0
        return len(self.data)

    def set_order(self, ord=None):
        """
        Сортировка для UPDATE
        :param ord:
        :return:
        """
        if ord:
            self.order = f"order by {ord}"
        else:
            self.order = ''

    def set_filter(self, flt=None):
        """
        Фильтр для UPDATE
        :param flt: строка для WHERE
        :return:
        """
        if flt:
            self.filter = f"where {flt}"
        else:
            self.filter = ''
        self.update()

    def set_sql(self, sql=None, flt=None):
        """
        Описание конкретной таблицы
        :param sql: SQL запрос для UPDATE
        :param flt: фильтр для UPDATE
        :return:
        """
        pass

    def update(self):
        """
        Обновление данных из БД SQL для визуализации
        :return:
        """
        if self.sql is not None:
            try:
                sql = f"""{self.sql} {self.filter} {self.order}"""
                if Const.TEST_MODE:
                    self.logfile.to_log(f"""start try [update class] \n{sql}""")
                ret = self.cur.execute(sql).fetchall()
            except pyodbc.OperationalError:
                self.logfile.to_log(f"""\n{'-'*20}\nРазрыв связи\n{'-'*20}""")
                sys.exit()
            except (sqlite3.Error, sqlite3.Warning) as err:
                self.logfile.to_log(f"""{err} [update class] \n{sql}""")
                # print(err, '[update class]', sql)
                ret = None
            if ret:
                self.header = [i[0] for i in self.cur.description]
                self.data = [['' if zp == None else zp for zp in rec] for rec in ret]
            else:
                self.data =[[]]
            self.tmodel = MyTableModel(self.header, self.data, self.editable, self.date_col)
            self.tmodel.need_save.connect(self.update_model)
            return len(self.data)
        else:
            return 0

    def update_model(self):
        """
        Обновление модели для визуальных виджетов
        :return:
        """
        self.rec_update(self.data[self.tmodel.current_index[0]][0],
                        {self.keys[self.tmodel.current_index[1] - 1][0]:
                             self.data[self.tmodel.current_index[0]][self.tmodel.current_index[1]]}
                        )
        self.need_to_save.emit()

    def model(self):
        """
        Вернуть созданную модель
        :return:
        """
        return self.tmodel

    def commit(self):
        """
        COMMIT изменений в БД
        :return:
        """
        try:
            self.con.commit()
            Const.IN_TRANSACTION = False
        except pyodbc.OperationalError:
            self.logfile.to_log(f"""\n{'-' * 20}\nРазрыв связи\n{'-' * 20}""")
            sys.exit()
        except (sqlite3.Error, sqlite3.Warning) as err:
            self.logfile.to_log(f"""{err} [commit]""")
            # self.log.out(str(datetime.date), str(datetime.time), '[commit]', str(err), '')
            # print(err, '[commit]')

    def rollback(self):
        """
        ROLLBACK изменений в БД
        :return:
        """
        try:
            self.con.rollback()
            Const.IN_TRANSACTION = False
        except pyodbc.OperationalError:
            self.logfile.to_log(f"""\n{'-' * 20}\nРазрыв связи\n{'-' * 20}""")
            sys.exit()
        except (sqlite3.Error, sqlite3.Warning) as err:
            # self.log.out(str(datetime.date), str(datetime.time), '[rollback]', str(err), '')
            self.logfile.to_log(f"""{err} [rollback]""")
            # print(err, '[rollback]')

    def rec_update(self, id, arg: dict):
        """
        Обновление записи в БД
        :param id: ID записи
        :param arg: список кортежей для корректировки
        :return:
        """
        args = ', '.join([f"{item[0]} = '{item[1]}'" for item in arg.items()])
        sql = f"update {self.dbname} set {args} where id = {id}"
        try:
            if Const.TEST_MODE:
                self.logfile.to_log(f"""Start try [update record] \n{sql}""")
            self.cur.execute(sql)
            Const.IN_TRANSACTION = True
        except pyodbc.OperationalError:
            self.logfile.to_log(f"""\n{'-' * 20}\nРазрыв связи\n{'-' * 20}""")
            sys.exit()
        except (sqlite3.Error, sqlite3.Warning) as err:
            # self.log.out(str(datetime.date), str(datetime.time), '[update record]', str(err), self.sql)
            self.logfile.to_log(f"""{err} [update record] \n{sql}""")
            # print(err, '[update record]', sql)
        return True

    def rec_append(self, arg: dict):
        """
        Добавление записи в таблицу
        :param arg: словарь данных для записи в БД
        :return:
        """
        key = ', '.join(arg.keys())
        val = f""" '{"', '".join(arg.values())}' """
        sql = f"""insert into {self.dbname} ({key}) values ({val})"""
        try:
            if Const.TEST_MODE:
                self.logfile.to_log(f"""Start try [append record] \n{sql}""")
            self.cur.execute(sql)
            Const.IN_TRANSACTION = True
        except pyodbc.OperationalError:
            self.logfile.to_log(f"""\n{'-' * 20}\nРазрыв связи\n{'-' * 20}""")
            sys.exit()
        except (sqlite3.Error, sqlite3.Warning) as err:
            # self.log.out(str(datetime.date), str(datetime.time), '[append record]', str(err), self.sql)
            self.logfile.to_log(f"""{err} [append record] \n{sql}""")
            # print(err, '[append record]', sql)
        return True

    def rec_delete(self, id):
        """
        Удаление записи
        :param id: ID записи для удаления
        :return:
        """
        sql = f"delete from {self.dbname} where id = {id}"
        try:
            if Const.TEST_MODE:
                self.logfile.to_log(f"""Start try [delete record] \n{sql}""")
            self.cur.execute(sql)
            Const.IN_TRANSACTION = True
        except pyodbc.OperationalError:
            self.logfile.to_log(f"""\n{'-' * 20}\nРазрыв связи\n{'-' * 20}""")
            sys.exit()
        except (sqlite3.Error, sqlite3.Warning) as err:
            self.logfile.to_log(f"""{err} [delete record] \n{sql}""")
            # print(err, '[delete record]', sql)
        return True

    def get_record(self, id):
        """
        Получить запись таблицы по ID
        :param id: ID записи
        :return:
        """
        fields = ', '.join([key[0] for key in self.keys])
        sql = f"select {fields} from {self.dbname} where id = {id}"
        cur = self.con.cursor()
        data = None
        try:
            if Const.TEST_MODE:
                self.logfile.to_log(f"""Start try [get record] \n{sql}""")
            data = cur.execute(sql).fetchone()
        except pyodbc.OperationalError:
            self.logfile.to_log(f"""\n{'-' * 20}\nРазрыв связи\n{'-' * 20}""")
            sys.exit()
        except (sqlite3.Error, sqlite3.Warning) as err:
            # self.log.out(str(datetime.date), str(datetime.time), '[get record]', str(err), self.sql)
            self.logfile.to_log(f"""{err} [get record] \n{sql}""")
            # print(err, '[get record]', sql)
        if not data:
            data = [''] * len(self.keys)
        ret = []
        for i, key in enumerate(self.keys):
            key = list(key)
            key.append(data[i])
            ret.append(key)
        return ret

    def execute_command(self, sql):
        """
        Исполнение произвольной команды SQL
        :param sql: SQL команда
        :return:
        """
        cur = self.con.cursor()
        try:
            if Const.TEST_MODE:
                self.logfile.to_log(f"""Start try [execute command] \n{sql}""")
            ret = cur.execute(sql).fetchall()
        except pyodbc.OperationalError:
            self.logfile.to_log(f"""\n{'-' * 20}\nРазрыв связи\n{'-' * 20}""")
            sys.exit()
        except (sqlite3.Error, sqlite3.Warning) as err:
            # self.log.out(str(datetime.date), str(datetime.time), '[execute command]', str(err), self.sql)
            self.logfile.to_log(f"""{err} [execute command] \n{sql}""")
            # print(err, '[execute command]', sql)
            ret = [[]]
        return ret


if __name__ == '__main__':
    pass