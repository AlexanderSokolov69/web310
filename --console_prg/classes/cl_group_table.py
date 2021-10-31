from .cl__main_sqlobject import SQLObject
from classes.cl_const import Const

class GroupTable(SQLObject):
    def set_sql(self, sql=None, ord='id'):
        self.keys = (
            ('idGroups', 'Учебная группа:'),
            ('idUsers', 'Фамилия И.О. кубиста:'),
            ('comment', 'Дополнительная информация:')
        )
        self.dbname = 'group_table'
        if sql is None:
            self.sql = f"""select t.id as 'id', rtrim(g.name) as 'Группа', rtrim(u.name) as 'Фамилия И.О.', 
                    t.comment as 'Комментарий' 
                from group_table t
                join groups g on g.id = t.idGroups
                join users u on u.id = t.idUsers"""
        else:
            self.sql = f"""{sql}"""
        self.set_order(ord)
