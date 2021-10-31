import sys
from PyQt5 import QtSql
from PyQt5.QtSql import QSqlQuery, QSqlDatabase
from PyQt5.QtWidgets import QApplication

from classes.cl_const import Const
from classes.cl_logwriter import LogWriter


class TSqlQuery(QSqlQuery):
    table_name = ''
    prepare_str_def = ''
    date_col_def = []

    def __init__(self, params=None, dsort=None):
        super(TSqlQuery, self).__init__()
        self.flog = LogWriter()
        self.prepare_str_modify()
        self.date_col = self.date_col_def.copy()
        self.param_str = []
        self.sort_str = ''
        self.cache = []
        if params:
            self.set_param_str(params)
        if dsort:
            self.set_sort_str(dsort)

    def prepare_str_modify(self, appstr=None):
        if appstr:
            self.prepare_str = f"""{self.prepare_str_def} {appstr}"""
        else:
            self.prepare_str = self.prepare_str_def[:]

    # def execute_command(self, sql):
    #     cur = QSqlQuery()
    #     if cur.exec(sql):
    #         cur.first()
    #         spis = []
    #         while cur.isValid():
    #             s = []
    #             for i in range(cur.record().count()):
    #                 s.append(cur.record().value(i))
    #             spis.append(s)
    #             cur.next()
    #         return spis
    #     else:
    #         return []


    def get_record(self, id_rec):
        sql = f"select * from {self.table_name} where id = {id_rec}"
        cur = super()
        ret = cur.exec(sql)
        if Const.TEST_MODE:
            self.flog.to_log(f"""SQL exec: {super().lastQuery()}""")
            if  ret:
                self.flog.to_log(f""" Ok""")
            else:
                self.flog.to_log(f""" WRONG!!!""")
        if ret:
            cur.first()
            s = []
            for i in range(cur.record().count()):
                s.append([cur.record().fieldName(i), '', cur.record().value(i)])
            return s
        else:
            return None

    def rec_append(self, args: dict):
        k = []
        v = []
        for key in args.keys():
            k.append(key)
            v.append(args[key])
        if key:
            sql = f"""insert into {self.table_name}({', '.join(k)})
                    values ({', '.join(['?' for _ in v])})"""
            super().prepare(sql)
            for val in v:
                super().addBindValue(val)
            ret = super().exec()
            if Const.TEST_MODE:
                self.flog.to_log(f"""SQL exec: {super().lastQuery()}""")
                if  ret:
                    self.flog.to_log(f"""Params: {v}\nResult: Ok""")
                else:
                    self.flog.to_log(f"""Params: {v}\nResult: WRONG!!!""")
            return ret
        return False

    def rec_delete(self, id):
        sql = f"""delete from {self.table_name} where id = {id}"""
        ret = super().exec(sql)
        if Const.TEST_MODE:
            self.flog.to_log(f"""SQL exec: {super().lastQuery()}""")
            if  ret:
                self.flog.to_log(f"""Params: {id}\nResult: Ok""")
            else:
                self.flog.to_log(f"""Params: {id}\nResult: WRONG!!!""")
        return ret

    def query_to_list(self, sql):
        ret = super().exec(sql)
        if Const.TEST_MODE:
            self.flog.to_log(f"""SQL exec: {super().lastQuery()}""")
            if  ret:
                self.flog.to_log(f"""Params: {self.param_str}\nResult: Ok""")
            else:
                self.flog.to_log(f"""Params: {self.param_str}\nResult: WRONG!!!""")
        self.data_to_cache()
        return self.cache

    def query_one_to_list(self, sql):
        ret = super().exec(sql)
        if Const.TEST_MODE:
            self.flog.to_log(f"""SQL exec: {super().lastQuery()}""")
            if  ret:
                self.flog.to_log(f"""Params: {self.param_str}\nResult: Ok""")
            else:
                self.flog.to_log(f"""Params: {self.param_str}\nResult: WRONG!!!""")
        self.data_to_cache()
        return [val[0] for val in self.cache]

    def set_param_str(self, spis=None):
        self.param_str = spis

    def set_sort_str(self, sort=None):
        if sort:
            self.sort_str = sort

    def refresh_select(self):
        super().finish()
        if self.sort_str:
            prep = f"{self.prepare_str} order by {', '.join(self.sort_str)}"
        else:
            prep = self.prepare_str
        super().prepare(prep)
        for prm in self.param_str:
            super().addBindValue(prm)
        super().setForwardOnly(True)
        ret = super().exec()
        self.data_to_cache()
        if Const.TEST_MODE:
            self.flog.to_log(f"""SQL exec: {super().lastQuery()}""")
            if  ret:
                self.flog.to_log(f"""Params: {self.param_str}\nResult: Ok""")
            else:
                self.flog.to_log(f"""Params: {self.param_str}\nResult: WRONG!!!""")
        return ret

    def data_to_cache(self):
        self.first()
        self.cache.clear()
        while self.isValid():
            s = []
            for i in range(self.record().count()):
                s.append(self.record().value(i))
            self.cache.append(s)
            self.next()

    def rows(self):
        return len(self.cache)

    def rec_update(self, id, arg):
        args = ', '.join([f"""{item[0]} = '{item[1]}' """ for item in arg.items()])
        sql = f"update {self.table_name} set {args} where id = {id}"
        super().exec(sql)
        return self.commit_table()

    def commit_table(self):
        return QSqlDatabase.commit(Const.DB)

    def rollback_table(self):
        return QSqlDatabase.rollback(Const.DB)


class QUsers(TSqlQuery):
        table_name = 'users'
        prepare_str_def = """select u.id, trim(u.name) as 'Фамилия И.О.', u.fam as 'Фамилия', u.ima as 'Имя', 
                u.otch as 'Отчество', u.login as 'Логин', u.phone as 'Телефон', 
                u.email as 'E-mail', u.birthday as 'Д.рожд', u.sertificate as 'Сертификат ПФДО',
                r.name as 'Роль', p.name as 'Место учёбы/работы', p.comment as 'Класс/Должн.',
                u.comment as 'Доп.информация'
               from users u
               join roles r on u.idRoles = r.id
               join places p on u.idPlaces = p.id
               join priv pp on pp.id = r.idPriv
               where pp.access like ?
        """


class QGroups(TSqlQuery):
    table_name = 'groups'
    prepare_str_def = """select g.id, trim(g.name) as 'Группа', trim(c.name) as 'Учебный курс', c.volume as 'Объем', 
                    c.lesson as 'Занятие', c.year as 'Уч.год', u.name as 'ФИО наставника', 
                    trim(g.comment) as 'Доп. информация' 
                from groups g
                join users u on g.idUsers = u.id
                join courses c on g.idCourses = c.id
                where c.year = ? and u.id = ?"""


class QGroupTables(TSqlQuery):
    table_name = 'group_table'
    prepare_str_def = f"""select t.id as 'id', g.name as 'Группа', u.name as 'Фамилия И.О.', 
                    t.comment as 'Комментарий', t.idUsers as 'UID', t.idGroups as 'GID',
                    u.navigator
                from group_table t
                join groups g on g.id = t.idGroups
                join users u on u.id = t.idUsers
                join (select cu.id, cu.acchour, cu.hday, cu.year from courses cu) jc on jc.id = g.idCourses
                where t.idGroups = ?"""


class QJournals(TSqlQuery):
    table_name = 'journals'
    prepare_str_def = f"""select j.id, j.date as 'Дата', rtrim(j.name) as 'Тема занятия', j.tstart as 'Время нач.', 
                    j.tend as 'Время оконч.', j.present as 'Посещаемость', j.estim as 'Оценки',
                     j.shtraf as 'Статусы', trim(j.comment) as 'Доп. информация', trim(j.usercomm) as 'Ученики', 
                     j.idGroups as 'IDG'
                from journals j
                join groups g on g.id = j.idGroups
                join (select cu.id, cu.acchour, cu.hday, cu.year from courses cu) jc on jc.id = g.idCourses
                where j.idGroups = ? """


class QStatisticsOne(TSqlQuery):
    table_name = None
    prepare_str_def = f"""select sum(c.hday) from groups g
            join courses c on g.idCourses = c.id
            join rasp r on r.idGroups = g.id
            where c.year = ? and g.idUsers = ?"""


class QRasp(TSqlQuery):
    table_name = 'rasp'
    prepare_str_def = f"""select r.id, TRIM(g.name) + ' - ' + trim(ju.name) as 'Группа - наставник', d.name as 'День недели' , 
                    k.name as 'Кабинет', r.tstart as 'Начало', r.tend as 'Окончание', 
                    jc.acchour as 'Акк. час', jc.hday as 'Занятий в день', trim(r.comment) as 'Доп. информация', 
                    r.idGroups as 'Группа', d.id as 'День'
                from rasp r
                join kabs k on r.idKabs = k.id
                join days d on r.idDays = d.id
                join groups g on r.idGroups = g.id
                join (select gu.id, u.name from groups gu join users u on gu.idUsers = u.id) ju on ju.id = g.id
                join (select cu.id, cu.acchour, cu.hday, cu.year from courses cu) jc on jc.id = g.idCourses
                where jc.year = ? """

    def get_record(self, id_rec):
        sql = f"select idDays, idKabs, tstart, tend from {self.table_name} where id = {id_rec}"
        cur = super()
        cur.exec(sql)
        cur.first()
        keys = [('id', 'id'),
                ('idDays', 'День недели:'),
                ('idKabs', 'Кабинет:'),
                ('tstart', 'Начало:'),
                ('tend', 'Окончание:'),]
        s = []
        for i in range(len(keys)):
            try:
                val = cur.record().value(i)
            except:
                val = None
            s.append([keys[i][0], keys[i][1], val])
        return s



if __name__ == '__main__':
    conn_str = 'Driver=SQL Server;Server=172.16.1.12,1433;Database=Journal4303;UID=sa;PWD=Prestige2011!;'
    app = QApplication(sys.argv)
    db =  QtSql.QSqlDatabase.addDatabase('QODBC')
    db.setDatabaseName(conn_str)
    if db.open():
        if Const.TEST_MODE:
            print('Connect: Ok')

        usr = QUsers(params=(Const.ACC_PREPOD,))
        usr.refresh_select()
        usr.first()
        print(usr.value(1))