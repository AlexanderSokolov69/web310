import datetime

from data import db_session
from data.cl_const import Const
from data.db_class_journals import Journals


class MyDict(dict):
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __getattr__(self, item):
        return self.get(item, None)

    def __getitem__(self, item):
        return self.get(item, None)

    def __repr__(self):
        res = []
        for k in self.keys():
            res.append(f"{k}: {self[k]}")
        return f"<MyDict({' | '.join(res)})"


def spis_to_dic(spis):  # format: "int='comment' int='comment' ..."
    dic = MyDict()
    if isinstance(spis, str):
        for rec in spis.split():
            k, v = rec.split('=')
            dic[int(k)] = v
    return dic


def date_us_ru(data):
    """
    Перевод US даты в RU
    :param data:
    :return:
    """
    data = str(data).strip()
    ret = data
    if len(data) == 10:
        try:
            ret = f"{int(data[8:10:1]):02}.{int(data[5:7:1]):02}.{int(data[0:4:1]):04}"
        except ValueError:
            pass
            # print('error in date_us_ru(data)')
    return ret


def date_ru_us(data):
    """
    Перевод RU даты в US
    :param data:
    :return:
    """
    tst = str(data).strip()
    ret = '1900-01-01'
    if len(tst) > 0:
        try:
            if len(tst) == 4:
                tst = f"01.01.{int(tst):04}"
            elif 0 < len(tst) < 3:
                tst = f"01.01.20{int(tst):02}"
            ret = f"{int(tst[6:10:1]):04}-{int(tst[3:5:1]):02}-{int(tst[0:2:1]):02}"
        except ValueError:
            pass
            # print('error in date_ru_us(data)')
    return ret


def get_days_list(days: dict, mon=9):
    def next_first_date(d: datetime):
        month = (d.month) % 12 + 1
        year = d.year + (month == 1)
        return datetime.date(year, month, 1)

    if mon > 8:
        year = Const.YEAR
    else:
        year = Const.YEAR + 1
    d1 = datetime.date(year, mon, 1)
    d2 = next_first_date(d1)
    ret = []
    oneday = datetime.timedelta(1)
    while d1 < d2:
        for day in days.values():
            if (d1.weekday() + 1) == day[0]:
                ret.append([str(d1), day[1:]])
        d1 += oneday
    return ret


def journ_fill_month(*args, **kwargs):
        month = kwargs['month']
        idGroups = kwargs['idGroups']
        rasp = kwargs['rasp']
        journ = kwargs['journ']
        list_days = MyDict()
        if rasp.count() > 0:
            for i, item in enumerate(rasp):
                list_days[item.idDays] = [item.idDays, item.tstart, item.tend]
            list_days = get_days_list(list_days, month)
            test = [] if len(journ) == 0 else [(date_ru_us(day.date), day.tstart) for day in journ]
            for rec in list_days:
                if (rec[0], rec[1][0]) not in test:
                    new_r = {}
                    new_r['idGroups'] = idGroups
                    new_r['date'] = rec[0]
                    new_r['name'] = 'Тема...'
                    new_r['tstart'] = rec[1][0]
                    new_r['tend'] = rec[1][1]
                    with db_session.create_session() as db_sess:
                        db_sess.add(Journals(**new_r))
                        db_sess.commit()


def journ_clear_month(*args, **kwargs):
    for rec in kwargs['journ']:
        if len(rec.name) < 9:
            if Const.TEST_MODE:
                print('DELETE', rec)
            with db_session.create_session() as db_sess:
                to_del = db_sess.query(Journals).get(rec.id)
                db_sess.delete(to_del)
                db_sess.commit()


class Checker():
    def __init__(self, flag=True):
        self.flag = flag

    def time(self, field):
        try:
            l, r = field.split(':')
            ret = f"{int(l):02}:{int(r):02}"
            self.flag = any([6 < int(l) < 22, 0 <= int(r) < 60])
            return Checker(self.flag)
        except Exception:
            print('time', field)
            return Checker(False)

    def date_us(self, field):
        try:
            y, m, d = field.split('-')
            dd = f"{int(y)}-{int(m)}-{int(d)}"
            self.flag = all([int(y) > 2019, 0 < int(m) < 13, 0 < int(d) < 32])
            dd = datetime.date(int(y), int(m), int(d))
            return Checker(self.flag)
        except Exception:
            print('date_us', field)
            return Checker(False)

    def date_ru(self, field):
        try:
            d, m, y = field.split('.')
            dd = f"{int(y)}.{int(m)}.{int(d)}"
            self.flag = all([int(y) > 2019, 0 < int(m) < 13, 0 < int(d) < 32])
            dd = datetime.date(int(y), int(m), int(d))
            return Checker(self.flag)
        except Exception:
            print('date_ru', field)
            return Checker(False)


if __name__ == '__main__':
    d = MyDict(attr='32')

    print(str(d))
