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
        return '\n'.join(res)


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
        for day in days:
            if (d1.weekday() + 1) == day[0]:
                ret.append([str(d1), day[1:]])
        d1 += oneday
    return ret


def journ_add(*args, **kwargs):
        month = kwargs['month']
        rasp = kwargs['rasp']
        journ = kwargs['journ']
        list_days = MyDict()
        if rasp.count() > 0:
            for i, item in enumerate(rasp):
                list_days[item.idDays] = [item.idDays, item.tstart, item.tend]
            list_days = get_days_list(list_days, month)
            test = [] if journ.count() == 0 else [day.data for day in journ]
            for rec in list_days:
                if rec[0] not in test:
                    arg = MyDict()
                    arg['idGroups'] = rasp[0].idGroups
                    arg['date'] = rec[0]
                    arg['name'] = 'Тема...'
                    arg['tstart'] = rec[1]
                    arg['tend'] = rec[2]
                    with db_session.create_session() as db_sess:
                        db_sess.append(Journals(arg))
                        db_sess.commit()


"""
    object = self.sender().objectName()
    if object == 'tab4_del_journ':
        del_cnt = 0
        id_select = []
        for index in self.tab4_journ_view.selectedIndexes():
            if index.column() == Const.JRN_DATE:
                if len(self.journ.cache[index.row()][Const.JRN_THEME].strip()) < 9:
                    id = self.journ.cache[index.row()][Const.JRN_ID]
                    self.journ.rec_delete(id)
                    del_cnt += 1
                else:
                    self.message_out.emit(
                        f"Невозможно удалить запись журнала: "
                        f"'{self.journ.cache[index.row()][Const.JRN_THEME].strip()}'")
        if del_cnt:
            self.journ_update()
"""

if __name__ == '__main__':
    d = MyDict(attr='32')

    print(str(d))
