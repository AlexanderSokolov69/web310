from .cl__main_sqlobject import SQLObject
from classes.cl_const import Const


class Roles(SQLObject):
    def set_sql(self, sql=None, ord='id'):
        self.keys = (
            ('name', 'Роль пользователя:'),
            ('idPriv', 'Привилегия доступа:'),
            ('comment', 'Комментарий:')
        )
        self.dbname = 'roles'
        if sql is None:
            self.sql = f"""select r.id as 'id', rtrim(r.name) as 'Наименование', p.name as 'Привилегии', 
               r.comment as 'Коментарий'
               from roles r
               join priv p on p.id = r.idPriv"""
        else:
            self.sql = f"""{sql}"""
        self.set_order(ord)
