import datetime
import sqlite3
import sys
from datetime import datetime
from configparser import ConfigParser
import pyodbc

from classes.cl_const import Const
from classes.cl_logwriter import LogWriter


class Sql:
    def __init__(self, conn):
        user = 'sa'
        password = 'Prestige2011!'
        str_con = f"""{conn};UID={user};PWD={password};"""
        if Const.TEST_MODE:
            print('pyodbc:', str_con)
        self.cnxn = pyodbc.connect(str_con)
        self.query = "-- {}\n\n-- Made in Python".format(datetime.now()
                                                         .strftime("%d/%m/%Y"))

    def get_connect(self):
        return self.cnxn


class ConnectDb:
    def __init__(self, path=None):
        flog = LogWriter()
        self.path = path
        self.con = None
        try:
            cfg = ConfigParser()
            if path:
                cfg.read(path, encoding='utf8')
            else:
                cfg.read('settings.ini')
            self.connect_type = cfg.get("Settings", "connect_type")
            if self.connect_type.lower() in ('odbc', ):
                connect_str = cfg.get("Settings", "odbc")
            else:
                db_name = cfg.get("Settings", "db_name")
                srv_name = cfg.get("Settings", "srv_name")
                srv_port = cfg.get("Settings", "srv_port")
                connect_str = f"Driver=SQL Server;Server={srv_name},{srv_port};Database={db_name}"

            Const.YEAR = int(cfg.get("Settings", "l_year"))
            Const.D_START = cfg.get("Settings", "otch_start")
            Const.D_END = cfg.get("Settings", "otch_end")

        except FileNotFoundError:
            flog.to_log(f"""Не найден файл [settings.ini]""")
            sys.exit()
        except ConfigParser:
            flog.to_log(f"""Нарушена структура файла [settings.ini]""")
            sys.exit()

        try:
            flog.to_log(f""" Старт подключения БД: {connect_str}""")
            self.con = self.toSql(connect_str).get_connect()
            flog.to_log(f"""Подключена БД: {connect_str}""")
            # print('Подключена БД:',  path)
        except Exception as err:
            flog.to_log(f"""СТОП!!! \n\t{err} \n\tПодключение не удалось {connect_str}""")
            sys.exit()

    def toSql(self, connect_str):
        return Sql(connect_str)

    def get_con(self):
        return self.con

if __name__ == '__main__':
    pass
   #con = ConnectDb('../settings.ini').get_con()
    #print(con)
    # conn = pyodbc.connect('DSN=it-cube64;UID=sa;PWD=Prestige2011!')

       # = pyodbc.connect("Driver=SQL Server; Server=172.16.1.12,1433; Database=master; UID = 'sa'; PWD = 'Prestige2011!';")