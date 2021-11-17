import datetime

from flask import g, session

from data.cl_const import Const
from data.db_class_courses import Courses
from data.db_class_group_table import GroupTable
from data.db_class_groups import Groups
from data.db_class_journals import Journals
from data.db_class_monts import Monts
from data.db_class_users import Users
from data.misc import MyDict, date_us_ru, check_access


class Statistics:
    def __init__(self, *args, **kwargs):
        self.date_from = kwargs.get('date_from', f'{Const.YEAR}-{Const.DATE_FROM}')
        self.date_to = kwargs.get('date_to', f'{Const.YEAR + 1}-{Const.DATE_TO}')
        self.idGroups = kwargs.get('idGroups', None)
        self.idCourses = kwargs.get('idCourses', None)
        self.idUsers = kwargs.get('idUsers', None)
        self.group_name = None
        self.course_name = None
        self.prepod_name = None
        self.users = None
        self.summary = MyDict()
        self.spisok_users = MyDict()
        users = kwargs.get('users', None)
        if not users and self.idGroups:
            users = g.db_sess.query(GroupTable).join(Users, GroupTable.idUsers == Users.id). \
                filter(GroupTable.idGroups == self.idGroups).order_by(Users.ima)
        self.user_spisok_create(users)

    def user_spisok_create(self, users):
        if users:
            for user in users:
                try:
                    item = MyDict()
                    item.idGroups = user.idGroups
                    item.pl_name = user.users.places.name.strip()
                    item.pl_comment = user.users.places.comment.strip()
                    item.id = user.users.id
                    item.name = user.users.name.rstrip()
                    if check_access([Const.AU_FULLNAME], snd=False):
                        item.ima_f = user.users.name.rstrip()
                    else:
                        item.ima_f = f"{user.users.ima.strip()} {user.users.fam[:2:1]}."
                    item.navigator = '1' in str(user.users.navigator)
                    item.klass = user.users.places.comment.strip()
                    self.spisok_users[user.id] = item
                except Exception as err:
                    print(err)

    def get_summary(self):
        return self.summary

    def get_pres_stat(self):
        if self.idGroups:
            pres_jrn = g.db_sess.query(Journals).join(GroupTable, GroupTable.idGroups == Journals.idGroups).\
                join(Groups, Groups.id == Journals.idGroups).join(Courses, Courses.id == Groups.idCourses).\
                filter(Journals.date.between(self.date_from, self.date_to)).\
                filter(Journals.idGroups == self.idGroups).order_by(Journals.date)
        else:
            pres_jrn = g.db_sess.query(Journals).join(GroupTable, GroupTable.idGroups == Journals.idGroups).\
                join(Groups, Groups.id == Journals.idGroups).join(Courses, Courses.id == Groups.idCourses).\
                filter(Journals.date.between(self.date_from, self.date_to))
            if self.idUsers:
                pres_jrn = pres_jrn.filter(Groups.idUsers == self.idUsers)
            if self.idCourses:
                pres_jrn = pres_jrn.filter(Groups.idCourses == self.idCourses)
            pres_jrn = pres_jrn.order_by(Journals.date)

            users = g.db_sess.query(GroupTable).join(Users, GroupTable.idUsers == Users.id).\
                join(Journals, GroupTable.idGroups == Journals.idGroups). \
                filter(Journals.date.between(self.date_from, self.date_to))
            # if self.idUsers:
            #     users = users.filter(Journals.groups.idUsers == self.idUsers)
            users = users.order_by(GroupTable.idGroups, Users.ima, Users.fam)
            # print('формируем self.spisok_users')
            self.user_spisok_create(users)
        # print('формируем статистику посещаемости')
        mnt_name = Monts().get_dict()
        presents = MyDict()
        groups = MyDict()
        try:
            for jrn in pres_jrn:
                groups[jrn.groups.id] = MyDict(group_name=f"{jrn.groups.name.strip()} {jrn.groups.comment.strip()}",
                                               course_name=jrn.groups.courses.name.strip(),
                                               prepod_name=jrn.groups.users.name.strip(),
                                               idGroups=int(jrn.groups.id),
                                               idCourses=int(jrn.groups.idCourses),
                                               idUsers=int(jrn.groups.idUsers)
                                               )
                if not self.group_name:
                    self.group_name = f"{jrn.groups.name.strip()} {jrn.groups.comment.strip()}"
                    self.course_name = jrn.groups.courses.name.strip()
                    self.prepod_name = jrn.groups.users.name.strip()
                try:
                    he, me = jrn.tend.split(':')
                    hs, ms = jrn.tstart.split(':')
                    lhours = (60 * int(he) + int(me) - 60 * int(hs) - int(ms)) // int(jrn.groups.courses.acchour)
                    res = {int(us) for us in jrn.present.split()}
                except Exception:
                    lhours = 0
                    res = {}
                item = presents.get(jrn.groups.id, MyDict())
                item[jrn.date] = MyDict(lhour=lhours, present=res)
                presents[jrn.groups.id] = item
        except Exception:
            pass
        # print('раскладываем статистику посещаемости по персоналиям')
        out_list = MyDict()
        pres_ids = set()
        users_set = set()
        users_set_nav = set()
        users_places = MyDict()
        users_pl_comment = MyDict()
        users_kvart = MyDict()

        for grp in presents.keys():
            ghead = MyDict()
            ghead.id = 'ID'
            ghead.navigator = 'Навигатор'
            ghead.ima_f = 'Имя Ф.'
            ghead.klass = 'Класс'
            ghead.stars = MyDict()
            ghead.stars_cnt = 0
            ghead.blacks_cnt = 0
            ghead.present = []
            out_list[grp] = MyDict(spis=[ghead],
                                   idGroups=groups[grp].idGroups,
                                   group_name=groups[grp].group_name,
                                   idCourses=groups[grp].idCourses,
                                   course_name=groups[grp].course_name,
                                   idUsers=groups[grp].idUsers,
                                   prepod_name=groups[grp].prepod_name,
                                   stars=MyDict()
                                   )

            for n in presents[grp].keys():
                dt = datetime.date.fromisoformat(n)
                out_list[grp].spis[0]['present'].append(f"{dt.day:02}.{dt.month:02}")

            for us in filter(lambda x: x.idGroups == grp, self.spisok_users.values()):
                head = MyDict()
                head.id = us.id
                head.navigator = us.navigator
                head.ima_f = us.ima_f
                head.klass = us.klass
                head.stars = MyDict()
                head.stars_cnt = 0
                head.blacks_cnt = 0
                head.present = []
                for d, item in zip (presents[grp].keys(), presents[grp].values()):
                    month = datetime.date.fromisoformat(d).month
                    pres = us.id in item.present

                    users_set.add(us.id)
                    users_pl_comment[us.pl_comment] = users_pl_comment.get(us.pl_comment, set())
                    users_pl_comment[us.pl_comment].add(us.id)
                    users_places[us.pl_name] = users_places.get(us.pl_name, set())
                    users_places[us.pl_name].add(us.id)
                    if us.navigator:
                        users_set_nav.add(us.id)
                    if pres:
                        pres_ids.add(us.id)

                    cnt = head.stars.get(month, ['', 0, 0, 0, 0])
                    cnt = [mnt_name[month], cnt[1] + 1, cnt[2] + pres, cnt[3] + item.lhour, cnt[4] + item.lhour * pres]
                    head.stars[month] = cnt
                    head.present.append(pres)
                out_list[grp].spis.append(head)
                for mnt in head.stars.keys():
                    new = head.stars[mnt]
                    curr = out_list[grp].stars.get(mnt, ['', 0, 0, 0, 0])
                    out_list[grp].stars[mnt] = [mnt_name[mnt],
                                                curr[1] + new[1],
                                                curr[2] + new[2],
                                                curr[3] + new[3],
                                                curr[4] + new[4]
                                                ]

            month = datetime.date.today().month
            for user in out_list[grp].spis[1:]:
                for star in user.stars:
                    if star != month:
                        dv = (user.stars[star][2] / user.stars[star][1])
                        user.stars_cnt += dv >= Const.PRESENT_PRC
                        user.blacks_cnt += dv < Const.PRESENT_PRC_LOW
                new_pres = []
                for dd, state in zip(out_list[grp].spis[0]['present'], user['present']):
                    mnt = int(dd.split('.')[1])
                    if  mnt in user.stars.keys():
                        dv = (user.stars[mnt][2] / user.stars[mnt][1])
                        if  dv >= Const.PRESENT_PRC:
                            state0 = [state, 'bg80']
                        elif dv < Const.PRESENT_PRC_LOW:
                            state0 = [state, 'bg20']
                        else:
                            state0 = [state, 'bg0']
                    else:
                        state0 = [state, 'bg0']
                    new_pres.append(state0)
                user['present'] = new_pres
            for mnt in out_list[grp].stars.keys():
                users_kvart[Const.KV[mnt]] = users_kvart.get(Const.KV[mnt], ['', 0, 0, 0, 0])
                if users_kvart[Const.KV[mnt]][0]:
                    users_kvart[Const.KV[mnt]][1] += out_list[grp].stars[mnt][1]
                    users_kvart[Const.KV[mnt]][2] += out_list[grp].stars[mnt][2]
                    users_kvart[Const.KV[mnt]][3] += out_list[grp].stars[mnt][3]
                    users_kvart[Const.KV[mnt]][4] += out_list[grp].stars[mnt][4]
                else:
                    users_kvart[Const.KV[mnt]] = out_list[grp].stars[mnt]
                try:
                    prc = round(100 * out_list[grp].stars[mnt][2] / out_list[grp].stars[mnt][1], 1)
                except ZeroDivisionError:
                    prc = 0
                out_list[grp].stars[mnt].append(prc)

        self.summary['kvart'] = users_kvart
        self.summary['kids_pres'] = len(pres_ids)
        self.summary['kids'] = len(users_set)
        self.summary['kids_nav'] = len(users_set_nav)
        self.summary.places = MyDict()

        for item in users_places.keys():
            users_places[item] = len(users_places[item])
        self.summary.pl_comment = MyDict()
        for item in sorted(users_places.items(), key=lambda x: x[1], reverse=True):
            self.summary.places[item[0]] = item[1]
        self.summary.pl_comment = MyDict()
        # ----------------------
        for kv in self.summary.kvart.items():
            self.summary.kvart[kv[0]][0] = kv[0]
            self.summary.kvart[kv[0]][5] = round(100 * kv[1][2] / kv[1][1], 1)

        def func(x):
            try:
                return int(x[0].split()[0])
            except Exception:
                return 0
        # ----------------------
        for item in sorted(users_pl_comment.items(), key=func):
            self.summary.pl_comment[item[0]] = len(item[1])
        if self.idGroups:
            return out_list[self.idGroups]
        return out_list

    def get_stat_grupped(self, *args, **kwargs):
        stat = self.get_pres_stat()
        result = MyDict()
        if kwargs:
            grp = kwargs['id']
        else:
            grp = None

        for item in stat.values():
            if grp:
                id = item[grp]
            else:
                id = 0
            cur = result.get(id, MyDict())
            if grp == 'idUsers':
                cur.course_name = item.prepod_name
            elif grp == 'idGroups':
                cur.course_name = item.group_name
            elif grp == 'idCourses':
                cur.course_name = item.course_name
            else:
                cur.course_name = 'Статистика по IT-кубу'

            cur.group_name = "Период:"
            cur.prepod_name = f"с {date_us_ru(self.date_from)} по {date_us_ru(self.date_to)}"
            cur.stars = cur.get('stars', MyDict())
            for mnt in item.stars.items():
                old = cur.stars.get(mnt[0], ['', 0, 0, 0, 0, 0])
                cur.stars[mnt[0]] = [mnt[1][0],
                                     old[1] + mnt[1][1],
                                     old[2] + mnt[1][2],
                                     old[3] + mnt[1][3],
                                     old[4] + mnt[1][4],
                                     round(100 * (old[2] + mnt[1][2]) / (old[1] + mnt[1][1]), 1)]
            result[id] = cur
        # print(result)
        return result

    def get_group_stat(self):
        uslist = self.get_pres_stat()
        mnt_name = Monts().get_dict()
        grp_days = MyDict()
        grp_days[0] = ['Период',
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

