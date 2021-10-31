from classes.t__sqlobject import TSQLObject
from classes.cl_const import Const

class STCourses(TSQLObject):
    def set_sql(self, sql=None, ord='id'):
        self.dbname = 'Courses'
        if sql is None:
            self.sql = f"""select id, name as 'Наименование курса', target as 'Возраст', volume as 'Объем',
                   lesson as 'Занятий/нед.', acchour as 'Академ.час', hday as 'Занятий в день', 
                   url as 'Ссылка на сайт', year as 'Учебный год' 
                from courses"""
        else:
            self.sql = f"""{sql}"""
        self.set_order(ord)


class STRasp(TSQLObject):
    def set_sql(self, sql=None, ord='g.id'):
        self.dbname = 'rasp'
        if sql is None:
            self.sql = f"""select r.id, RTRIM(g.name) + ' - ' + rtrim(ju.name) as 'Группа - наставник', d.name as 'День недели' , 
                    k.name as 'Кабинет', r.tstart as 'Начало', r.tend as 'Окончание', 
                    jc.acchour as 'Акк. час', jc.hday as 'Занятий в день', r.comment as 'Доп. информация', 
                    r.idGroups as 'ID Группа', d.id as 'ID День', jc.year as 'Уч.год',
                    ju.id as 'ID User', jc.id as 'ID Courses'
                from rasp r
                join kabs k on r.idKabs = k.id
                join days d on r.idDays = d.id
                join groups g on r.idGroups = g.id
                join (select gu.id, u.name from groups gu join users u on gu.idUsers = u.id) ju on ju.id = g.id
                join (select cu.id, cu.acchour, cu.hday, cu.year from courses cu) jc on jc.id = g.idCourses"""
            self.set_order('d.id, k.id, r.tstart')
        else:
            self.sql = f"""{sql}"""
            self.set_order(ord)


class STJournals(TSQLObject):
    def set_sql(self, sql=None, ord='j.date'):
        self.dbname = 'journals'
        if sql is None:
            self.sql = f"""select j.id, j.date as 'Дата', rtrim(j.name) as 'Тема занятия', j.tstart as 'Время нач.', 
                    j.tend as 'Время оконч.', j.present as 'Посещаемость', j.estim as 'Оценки',
                     j.shtraf as 'Штрафы', j.comment as 'Доп. информация', j.usercomm, j.idGroups as 'idGroups'
                from journals j
                join groups g on g.id = j.idGroups
                join (select cu.id, cu.acchour, cu.hday, cu.year from courses cu) jc on jc.id = g.idCourses"""
            self.set_order('j.date, j.tstart')
        else:
            self.sql = f"""{sql}"""
            self.set_order(ord)


class STUsers(TSQLObject):
    def set_sql(self, sql=None, flt=None):
        self.dbname = 'users'
        if sql is None:
            self.sql = f"""select u.id, rtrim(u.name) as 'Фамилия И.О.', u.fam as 'Фамилия', u.ima as 'Имя', 
                u.otch as 'Отчество', u.login as 'Логин', u.phone as 'Телефон', 
                u.email as 'E-mail', u.birthday as 'Д.рожд', u.sertificate as 'Сертификат ПФДО',
                r.name as 'Роль', p.name as 'Место учёбы/работы', p.comment as 'Класс/Должн.',
                u.comment as 'Доп.информация'
               from users u
               join roles r on u.idRoles = r.id
               join places p on u.idPlaces = p.id"""
        else:
            self.sql = f"""{sql}"""


class STGroups(TSQLObject):
    def set_sql(self, sql=None, ord='g.id'):
        self.dbname = 'groups'
        if sql is None:
            self.sql = f"""select g.id, rtrim(g.name) as 'Группа', rtrim(c.name) as 'Учебный курс', c.volume as 'Объем', 
                    c.lesson as 'Занятие', c.year as 'Уч.год', rtrim(u.name) as 'ФИО наставника',
                    g.idUsers, g.idCourses
                from groups g
                join users u on g.idUsers = u.id
                join courses c on g.idCourses = c.id"""
        else:
            self.sql = f"""{sql}"""
        self.set_order(ord)


class STGroupTable(TSQLObject):
    def set_sql(self, sql=None, ord='u.name'):
        self.dbname = 'group_table'
        if sql is None:
            self.sql = f"""select t.id as 'id', rtrim(g.name) as 'Группа', rtrim(u.name) as 'Фамилия И.О.', 
                    t.comment as 'Комментарий', t.idGroups, jc.acchour, jc.hday, t.idUsers
                from group_table t
                join groups g on g.id = t.idGroups
                join users u on u.id = t.idUsers
                join (select cu.id, cu.acchour, cu.hday, cu.year from courses cu) jc on jc.id = g.idCourses"""

        else:
            self.sql = f"""{sql}"""
        self.set_order(ord)
