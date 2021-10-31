from .cl__main_sqlobject import SQLObject
from classes.cl_const import Const


class Journals(SQLObject):
    def set_sql(self, sql=None, ord='j.date'):
        self.keys = (
            ('idGroups', 'Учебная группа:'),
            ('Date', 'Дата занятия'),
            ('name', 'Тема занятия:'),
            ('tstart', 'Начало занятий:'),
            ('tend', 'Окончание занятий:'),
            ('present', 'Отметки о посещении'),
            ('estim', 'Отметки'),
            ('shtraf', 'Штрафы'),
            ('comment', 'Доп. информация')
        )
        self.dbname = 'journals'
        if sql is None:
            self.sql = f"""select j.id, j.date as 'Дата', j.name as 'Тема занятия', j.tstart as 'Время нач.', 
                    j.tend as 'Время оконч.', j.comment as 'Доп. информация'
                from journals j"""
            self.set_order('j.date, j.tstart')
        else:
            self.sql = f"""{sql}"""
            self.set_order(ord)
