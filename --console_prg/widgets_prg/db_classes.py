from PyQt5 import QtSql

from classes.cl_const import Const
from classes.cl_logwriter import LogWriter


class QSqlObject(QtSql.QSqlQuery):
    def __init__(self):
        super(QSqlObject, self).__init__()
        self.logfile = LogWriter()
        self.obj = QtSql.QSqlQuery()
        self.on_prepare = None

    def refresh_select(self, lst=None, sort='u.name'):
        if lst is None:
            lst = []
    #    self.obj.finish()
        self.obj.prepare(self.on_prepare)
        for i, prm in enumerate(lst):
            self.obj.bindValue(i, prm)
        self.obj.bindValue(i + 1, sort)
        ret = self.obj.execBatch()
        if Const.TEST_MODE:
            self.logfile.to_log(f"""{self.obj.lastQuery()} \n {self.obj.boundValues()}""")
        return ret


class QPrepod(QSqlObject):
    def __init__(self):
        super(QPrepod, self).__init__()
        self.on_prepare = """select u.id, rtrim(u.name) as 'Фамилия И.О.', u.fam as 'Фамилия', u.ima as 'Имя', 
                u.otch as 'Отчество', u.login as 'Логин', u.phone as 'Телефон', 
                u.email as 'E-mail', u.birthday as 'Д.рожд', u.sertificate as 'Сертификат ПФДО',
                r.name as 'Роль', p.name as 'Место учёбы/работы', p.comment as 'Класс/Должн.',
                u.comment as 'Доп.информация', pr.access as 'priv'
               from users u
               join roles r on u.idRoles = r.id
               join places p on u.idPlaces = p.id
			   left join priv pr on pr.id = r.idPriv
"""
        #        			   where pr.access like ?
        # 			   order by ?
        # """
        self.help = {0: ["priv", 'Маска прав доступа'],
                     1: ["u.name", 'Поле сортировки']}