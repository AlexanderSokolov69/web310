from .cl__main_sqlobject import SQLObject
from classes.cl_const import Const


class Rasp(SQLObject):
    def set_sql(self, sql=None, ord='g.id'):
        self.keys = (
            ('idGroups', 'Учебная группа:'),
            ('idDays', 'День недели'),
            ('idKabs', 'Кабинет:'),
            ('tstart', 'Начало занятий:'),
            ('tend', 'Окончание занятий:'),
            ('comment', 'Доп. информация')
        )
        self.dbname = 'rasp'
        if sql is None:
            self.sql = f"""select r.id, RTRIM(g.name) + ' - ' + rtrim(ju.name) as 'Группа - наставник', d.name as 'День недели' , 
                    k.name as 'Кабинет', r.tstart as 'Начало', r.tend as 'Окончание', 
                    jc.acchour as 'Акк. час', jc.hday as 'Занятий в день', r.comment as 'Доп. информация', 
                    r.idGroups as 'Группа', d.id as 'День'
                from rasp r
                join kabs k on r.idKabs = k.id
                join days d on r.idDays = d.id
                join groups g on r.idGroups = g.id
                join (select gu.id, u.name from groups gu join users u on gu.idUsers = u.id) ju on ju.id = g.id
                join (select cu.id, cu.acchour, cu.hday from courses cu) jc on jc.id = g.idCourses"""
            self.set_order('d.id, k.id, r.tstart')
        else:
            self.sql = f"""{sql}"""
            self.set_order(ord)
