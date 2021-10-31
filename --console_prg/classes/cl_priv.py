import sqlite3
from .cl__main_sqlobject import SQLObject
from classes.cl_const import Const


class Privileges(SQLObject):
    def set_sql(self, sql=None, ord='id'):
        self.keys = (
            ('name', 'Название привилегии доступа:'),
            ('access', 'Код доступа:'),
            ('comment', 'Доп. информация')
        )
        self.dbname = 'priv'
        if sql is None:
            self.sql = f"""select id, name as 'Наименование', access as 'Привилегии'
               from priv"""
        else:
            self.sql = f"""{sql}"""
        self.set_order(ord)
