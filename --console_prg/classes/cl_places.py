import sqlite3
from .cl__main_sqlobject import SQLObject
from classes.cl_const import Const


class Places(SQLObject):
    def set_sql(self, sql=None, ord='Наименование'):
        self.keys = (
            ('name', 'Место работы/учёбы:'),
            ('comment', 'класс/доп.инф.:')
        )
        self.dbname = 'places'
        if sql is None:
            self.sql = f"""select id, name as 'Наименование', comment as 'Доп.инфо'
               from places"""
        else:
            self.sql = f"""{sql}"""
        self.set_order(ord)
