from .cl__main_sqlobject import SQLObject
from classes.cl_const import Const


class Groups(SQLObject):
    def set_sql(self, sql=None, ord='g.id'):
        self.keys = (
            ('name', 'Кодовое название учебной группы:'),
            ('idCourses', 'Учебная программа:'),
            ('idUsers', 'Фамилия И.О. наставника:'),
            ('comment', 'Доп. информация')
        )
        self.dbname = 'groups'
        if sql is None:
            self.sql = f"""select g.id, rtrim(g.name) as 'Группа', rtrim(c.name) as 'Учебный курс', c.volume as 'Объем', 
                    c.lesson as 'Занятие', c.year as 'Уч.год', u.name as 'ФИО наставника', g.comment as 'Доп. информация'
                from groups g
                join users u on g.idUsers = u.id
                join courses c on g.idCourses = c.id"""
        else:
            self.sql = f"""{sql}"""
        self.set_order(ord)
