import datetime

from flask import g

from data.cl_const import Const
from data.db_class_group_table import GroupTable
from data.db_class_journals import Journals
from data.misc import MyDict


class Statistics:
    def __init__(self, *args, **kwargs):
        self.date_from = kwargs.get('date_from', f'{Const.YEAR}-{Const.DATE_FROM}')
        self.date_to = kwargs.get('date_to', f'{Const.YEAR + 1}-{Const.DATE_TO}')
        self.idGroups = kwargs.get('idGroups', None)
        self.spisok_users = MyDict()
        if users := kwargs.get('users', None):
            for user in users:
                try:
                    item = MyDict()
                    item.id = user.id
                    item.name = user.name.strip()
                    item.ima_f = f"{user.ima.strip()} {user.fam[:2:1]}."
                    item.navigator = True if isinstance(user.navigator, str) and ('1' in user.navigator) else False
                    item.klass = user.places.comment.strip()
                    self.spisok_users[user.id] = item
                except Exception as err:
                    print(err)
        else:
            print('Создать выборку по всем кубистам...')

    def get_pres_stat(self):
        if self.idGroups:
            pres_jrn = g.db_sess.query(Journals).join(GroupTable, GroupTable.idGroups == Journals.idGroups).\
                filter(Journals.date <= self.date_to).\
                filter(Journals.idGroups == self.idGroups).order_by(Journals.date.desc())
        else:
            pres_jrn = g.db_sess.query(Journals).join(GroupTable, GroupTable.idGroups == Journals.idGroups).\
                filter(Journals.date <= self.date_to).\
                order_by(Journals.date.desc())

        presents = []
        try:
            for i, jrn in enumerate(pres_jrn):
                try:
                    res = [int(us) for us in jrn.present.split()]
                except Exception:
                    res = []
                presents.append((jrn.date, res))
                if i > 10:
                    break
        except Exception:
            pass
        uslist = []
        head = ['Навигатор', 'Имя Ф.', 'Класс']
        for n, _ in reversed(presents):
            dt = datetime.date.fromisoformat(n)
            head.append(f"{dt.day:02}.{dt.month:02}")
        uslist.append(head)
        for us in self.spisok_users.values():
            line = [us.navigator, us.ima_f, us.klass]
            for _, n in reversed(presents):
                line.append(us.id in n)
            uslist.append(line)
        return uslist
