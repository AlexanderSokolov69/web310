from classes.cl_const import Const
from .cl__main_sqlobject import SQLObject


class Courses(SQLObject):
    def set_sql(self, sql=None, ord='id'):
        self.keys = (
            ('name', 'Наименование учебного курса:'),
            ('target', 'Возрастная группа:'),
            ('volume', 'Объём курса в акк.часах:'),
            ('lesson', 'Занятий в нед.:'),
            ('acchour', 'Академ.час:'),
            ('hday', 'Занятий в день:'),
            ('url', 'Ссылка на раздел на сайте:'),
            ('year', 'Учебный год:')
        )
        self.dbname = 'Courses'
        if sql is None:
            self.sql = f"""select id, name as 'Наименование курса', target as 'Возраст', volume as 'Объем',
                   lesson as 'Занятий/нед.', acchour as 'Академ.час', hday as 'Занятий в день', url as 'Ссылка на сайт', year as 'Учебный год' 
                from courses"""
        else:
            self.sql = f"""{sql}"""
        self.set_order(ord)
