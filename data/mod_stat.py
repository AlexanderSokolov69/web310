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
        except Exception:
            pass
        uslist = []
        head = MyDict()
        head.navigator = 'Навигатор'
        head.ima_f = 'Имя Ф.'
        head.klass = 'Класс'
        head.stars = MyDict()
        head.stars_cnt = 0
        head.present = []
        for n, _ in reversed(presents):
            dt = datetime.date.fromisoformat(n)
            head.present.append(f"{dt.day:02}.{dt.month:02}")
        uslist.append(head)
        for us in self.spisok_users.values():
            head = MyDict()
            head.navigator = us.navigator
            head.ima_f = us.ima_f
            head.klass = us.klass
            head.stars = MyDict()
            head.stars_cnt = 0
            head.blacks_cnt = 0
            head.present = []
            for d, n in reversed(presents):
                month = datetime.date.fromisoformat(d).month
                pres = us.id in n
                cnt = head.stars.get(month, [0, 0])
                cnt = [cnt[0] + 1, cnt[1] + pres]
                head.stars[month] = cnt
                head.present.append(pres)
            uslist.append(head)
        month = datetime.date.today().month
        for user in uslist[1:]:
            for star in user.stars:
                if star != month:
                    user.stars_cnt += (user.stars[star][1] / user.stars[star][0]) >= Const.PRESENT_PRC
                    user.blacks_cnt += (user.stars[star][1] / user.stars[star][0]) < Const.PRESENT_PRC_LOW
            new_pres = []
            for dd, state in zip(uslist[0].present, user.present):
                mnt = int(dd.split('.')[1])
                if  mnt in user.stars.keys():
                    if (user.stars[mnt][1] / user.stars[mnt][0]) >= Const.PRESENT_PRC:
                        state0 = [state, 'bg80']
                    elif (user.stars[mnt][1] / user.stars[mnt][0]) < Const.PRESENT_PRC_LOW:
                        state0 = [state, 'bg20']
                    else:
                        state0 = [state, 'bg0']
                else:
                    state0 = [state, 'bg0']
                new_pres.append(state0)
            user.present = new_pres
        return uslist
