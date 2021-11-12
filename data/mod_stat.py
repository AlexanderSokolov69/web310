import datetime

from flask import g

from data.cl_const import Const
from data.db_class_courses import Courses
from data.db_class_group_table import GroupTable
from data.db_class_groups import Groups
from data.db_class_journals import Journals
from data.db_class_monts import Monts
from data.db_class_users import Users
from data.misc import MyDict


class Statistics:
    def __init__(self, *args, **kwargs):
        self.date_from = kwargs.get('date_from', f'{Const.YEAR}-{Const.DATE_FROM}')
        self.date_to = kwargs.get('date_to', f'{Const.YEAR + 1}-{Const.DATE_TO}')
        self.idGroups = kwargs.get('idGroups', None)
        self.group_name = None
        self.course_name = None
        self.prepod_name = None
        self.spisok_users = MyDict()
        if users := kwargs.get('users', None):
            pass
        elif self.idGroups:
            users = g.db_sess.query(Users).join(GroupTable). \
                filter(GroupTable.idGroups == self.idGroups).order_by(Users.ima)
        else:
            print('Создать выборку по всем кубистам...')
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

    def get_pres_stat(self):
        if self.idGroups:
            pres_jrn = g.db_sess.query(Journals).join(GroupTable, GroupTable.idGroups == Journals.idGroups).\
                join(Groups, Groups.id == Journals.idGroups).join(Courses, Courses.id == Groups.idCourses).\
                filter(Journals.date <= self.date_to).\
                filter(Journals.idGroups == self.idGroups).order_by(Journals.date.desc())
        else:
            pres_jrn = g.db_sess.query(Journals).join(GroupTable, GroupTable.idGroups == Journals.idGroups).\
                join(Groups, Groups.id == Journals.idGroups).join(Courses, Courses.id == Groups.idCourses).\
                filter(Journals.date <= self.date_to).\
                order_by(Journals.date.desc())

        presents = []
        try:
            for i, jrn in enumerate(pres_jrn):
                if not self.group_name:
                    self.group_name = f"{jrn.groups.name.strip()} {jrn.groups.comment.strip()}"
                    self.course_name = jrn.groups.courses.name.strip()
                    self.prepod_name = jrn.groups.users.name.strip()
                try:
                    he, me = jrn.tend.split(':')
                    hs, ms = jrn.tstart.split(':')
                    lhours = (60 * int(he) + int(me) - 60 * int(hs) - int(ms)) // int(jrn.groups.courses.acchour)
                    res = [int(us) for us in jrn.present.split()]
                except Exception:
                    lhours = 0
                    res = []
                presents.append((jrn.date, res, lhours))
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
        for n, _, __ in reversed(presents):
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
            for d, n, lh in reversed(presents):
                month = datetime.date.fromisoformat(d).month
                pres = us.id in n
                cnt = head.stars.get(month, [0, 0, 0, 0])
                cnt = [cnt[0] + 1, cnt[1] + pres, cnt[2] + lh, cnt[3] + lh * pres]
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

    def get_group_stat(self, idGroup=None):
        uslist = self.get_pres_stat()
        mnt_name = Monts().get_dict()
        grp_days = MyDict()
        grp_days[0] = ['Месяц',
                       'Списочная посещаемость',
                       'Фактическая посещаемость',
                       'Списочных чел/часов',
                       'Фактически чел/часов']
        for el in uslist:
            for mnt, pres in zip(el.stars.keys(), el.stars.values()):
                item = grp_days.get(mnt, ['', 0, 0, 0, 0])
                grp_days[mnt] = [mnt_name[mnt], item[1] + pres[0], item[2] + pres[1],
                                 item[3] + pres[2], item[4] + pres[3]]
        res = MyDict()
        for mnt, item in zip(grp_days.keys(), grp_days.values()):
            if mnt == 0:
                grp_days[mnt].append('% посещаемости')
            else:
                grp_days[mnt].append(f"{round(100 * item[2] / item[1], 1)}%")

        res.group_name = self.group_name
        res.course_name = self.course_name
        res.prepod_name = self.prepod_name
        res.stat = grp_days
        return res

