import datetime
from classes.cl_const import Const
from new_prg.db_connect import TSqlQuery


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


def qget_day_list():
    sql = "select name from days order by id"
    return TSqlQuery().query_one_to_list(sql)


def qget_short_day_list():
    sql = "select cname from days order by id"
    ret =  TSqlQuery().query_one_to_list(sql)
    return ret


def qget_time_list():
    sql = "select name from times order by id"
    return TSqlQuery().query_one_to_list(sql)


def qget_kab_list():
    sql = "select name, color from kabs order by id"
    return TSqlQuery().query_to_list(sql)

    # return [['21', (85, 85, 255)],
    #         ['22', (255, 0, 0)],
    #         ['24', (255, 170, 0)],
    #         ['25', (255, 255, 0)],
    #         ['27', (196, 0, 127)],
    #         ['28', (0, 170, 0)]]


def qget_monts_list():
    sql = f"""select num, name from monts order by id"""
    return TSqlQuery().query_to_list(sql)


def next_first_date(d: datetime):
    month = (d.month) % 12 + 1
    year = d.year + (month == 1)
    return datetime.date(year, month, 1)


def qget_days_list(days: dict, mon=9):
    if mon > 8:
        year = Const.YEAR
    else:
        year = Const.YEAR + 1
    d1 = datetime.date(year, mon, 1)
    d2 = next_first_date(d1)
    ret = []
    oneday = datetime.timedelta(1)
    while d1 < d2:
        if d1.weekday() in days.keys():
            ret.append([str(d1), *days[d1.weekday()]])
        d1 += oneday
    return ret


def get_prepod_list():
    sql = f"""select u.id, trim(u.name) as trimname from users u
               join roles r on u.idRoles = r.id
               join priv pp on pp.id = r.idPriv
               where pp.access like '{Const.ACC_PREPOD}'
               order by trimname"""
    return TSqlQuery().query_to_list(sql)