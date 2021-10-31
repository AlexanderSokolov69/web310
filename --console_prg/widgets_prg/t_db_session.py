from datetime import datetime

from PyQt5.QtSql import QSqlDatabase

from classes.cl_const import Const
from classes.db_session import ConnectDb


class QtSql:
    def __init__(self, conn):
        user = 'sa'
        password = 'Prestige2011!'
        str_con = f"""{conn};UID={user};PWD={password};"""
        if Const.TEST_MODE:
            print(str_con)
        self.db = QSqlDatabase().addDatabase('QODBC')
        self.db.setDatabaseName(str_con)
        Const.DB = self.db

    def get_connect(self):
        return self.db.open()


class QtConnectDb(ConnectDb):
    def toSql(self, connect_str):
        return QtSql(connect_str)
