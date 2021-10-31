import sys
import traceback as tb
import datetime
from classes.cl_const import Const
from classes.cl_logwriter import LogWriter

from classes.t_stat_tables import STUsers, STGroups, STRasp, STJournals, STGroupTable, STCourses
from PyQt5 import QtGui
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, pyqtSignal
from PyQt5.QtWidgets import QComboBox

from classes.bb_converts import date_us_ru
from classes.cl_const import Const
from classes.t__sqlobject import TSQLObject


def except_hook(cls, exception, traceback):
    global flog
    flog.to_log(f"""{exception} | \n{tb.format_tb(traceback)[0]}""")
    sys.__excepthook__(cls, exception, traceback)


class Statistics:
    def __init__(self, conn, user_id=None):
        self.con = conn
        self.user_id = user_id
        self.d_user = {}
        self.d_groups = {}
        self.d_rasp = {}
        self.d_journal = {}
        self.d_g_table = {}
        self.d_courses = {}
        self.full_struct = {}
        self.user = STUsers(self.con)
        self.groups = STGroups(self.con)
        self.rasp = STRasp(self.con)
        self.journal = STJournals(self.con)
        self.g_table = STGroupTable(self.con)
        self.courses = STCourses(self.con)
        self.update()

    def update(self):
        # courses
        self.d_courses = {}
        self.courses.set_filter(f"year = {Const.YEAR}")     # Courses - учебные курсы
        if self.courses.rows() > 0:
            for c in self.courses.data:
                rec = {'crsname': c[Const.CRS_NAME],            # Наименование курса
                       'target': c[Const.CRS_TARGET],           # Возрастной диапазон
                       'volume': c[Const.CRS_VOLUME],           # Объём курса
                       'lesson': c[Const.CRS_LESS],             # Занятий в неделю
                       'academh': c[Const.CRS_ACCH],            # Академический час
                       'hours': c[Const.CRS_HDAY],              # Занятий в неделю
                       'url': c[Const.CRS_URL],                 # URL - ссылка на описание
                       'year': c[Const.CRS_YEAR],               # Учебный год
                       'grupps': {}                             # Учебные группы курса
                       }
                self.d_courses[c[Const.CRS_ID]] = rec
        self.full_struct = self.d_courses.copy()

        # groups
        if self.user_id:
            self.groups.set_filter(f"g.idUsers={self.user_id} and c.year={Const.YEAR}")
        else:
            self.groups.set_filter(f"c.year={Const.YEAR}")  # Groups - Учебные группы
        self.d_groups = {}
        if self.groups.rows() > 0:
            for g in self.groups.data:
                rec = {'name': g[Const.GRP_NAME],           # Наименование учебной группы
                       'cname': g[Const.GRP_CNAME],         # Наименование курса
                       'volume': g[Const.GRP_VOL],          # Объём курса
                       'lesson': g[Const.GRP_LESS],         # Занятий в неделю
                       'year': g[Const.GRP_YEAR],           # Учебный год
                       'teacher': g[Const.GRP_FIO],         # ФИО наставника
                       'idUsers': g[Const.GRP_IDU],         # ID Наставника
                       'idCourses': g[Const.GRP_IDC]}       # ID Курса
                self.d_groups[g[Const.GRP_ID]] = rec
        # users
        if self.user_id:
            self.user.set_filter(f"u.id={self.user_id}")
        else:
            self.user.set_filter("u.id = (select gg.idUsers from groups gg where gg.idUsers = u.id)")
        self.d_user = {}
        if self.user.rows() > 0:                            # Users - Список лиц
            for u in self.user.data:
                rec = {'name': u[Const.USR_NAME],           # ФИО
                       'fam': u[Const.USR_FAM],             # Фамилия
                       'ima': u[Const.USR_IMA],             # Имя
                       'otch': u[Const.USR_OTCH],           # Отчество
                       'login': u[Const.USR_LOGIN],         # Логин доступа
                       'phone': u[Const.USR_PHONE],         # Телефон
                       'email': u[Const.USR_EMAIL],         # E-mail
                       'birthday': u[Const.USR_BIRTHDAY],   # Дата родления
                       'sert': u[Const.USR_SERT],           # ПФДО
                       'role': u[Const.USR_ROLE],           # Роль в системе
                       'place': u[Const.USR_PLACE],         # Место учёбы/работы
                       'dop': u[Const.USR_DOP]              # Класс/доп.информация
                       }
                self.d_user[u[Const.USR_ID]] = rec

        # rasp
        if self.user_id:
            self.rasp.set_filter(f"g.idUsers = {self.user_id} and jc.year = {Const.YEAR}")
        else:
            self.rasp.set_filter(f"jc.year = {Const.YEAR}")
        self.d_rasp = {}
        if self.rasp.rows() > 0:                            # Rasp - Расписания занятий
            for r in self.rasp.data:
                rec = {'name': r[Const.RSP_NAME],           # Уч.группа - наставник
                       'weekday': r[Const.RSP_WEEKNAME],    # День недели
                       'kabname': r[Const.RSP_KABNAME],     # Номер кабинета
                       'tstart': r[Const.RSP_START],         # Начало занятия
                       'tend': r[Const.RSP_END],             # Окончание занятий
                       'academh': r[Const.RSP_ACCH],        # Длит. академ. часа
                       'countless': r[Const.RSP_CNTLESS],   # Длительность урока, часов
                       'comment': r[Const.RSP_COMMENT],     # Доп. информация
                       'idGroups': r[Const.RSP_IDG],        # ID Группы
                       'idDay': r[Const.RSP_IDD],           # ID Дня
                       'year': r[Const.RSP_YEAR],           # Учебный год
                       'idUsers': r[Const.RSP_IDU],         # ID кубиста
                       'idCourses': r[Const.RSP_IDC]        # ID Курса
                       }
                self.d_rasp[r[Const.RSP_ID]] = rec
                # print(rec)

        # g_table
        if self.user_id:
            self.g_table.set_filter(f"g.idUsers = {self.user_id} and jc.year = {Const.YEAR}")
        else:
            self.g_table.set_filter(f"jc.year = {Const.YEAR}")
        self.d_g_table = {}
        if self.g_table.rows() > 0:                         # Group_table - Состав учебных групп
            for g in self.g_table.data:
                rec = {'gname': g[Const.GT_GNAME],          # Наименование группы
                       'studname': g[Const.GT_STUDNAME],    # ФИО кубиста
                       'comment': g[Const.GT_COMMENT],      # Доп. информация
                       'idGroups': g[Const.GT_IDG],         # ID Группы
                       'academh': g[Const.GT_ACCH],         # Длительность академ.часа
                       'hours': g[Const.GT_HDAY],           # Количество часов урока
                       'idUsers': g[Const.GT_IDU]           # ID Кубиста
                       }
                self.d_g_table[g[Const.GT_ID]] = rec

        # journ
        self.d_journal = {}
        if self.user_id:
            self.journal.set_filter(f"""g.idUsers = {self.user_id} and jc.year = {Const.YEAR}
                                    and j.date between '{Const.D_START}' and '{Const.D_END}' """)
        else:
            self.journal.set_filter(f"""jc.year = {Const.YEAR}
                                    and j.date between '{Const.D_START}' and '{Const.D_END}' """)
        if self.journal.rows() > 0:                         # Journals - Журнал занятий
            for j in self.journal.data:
                rec = {'date': j[Const.JRN_DATE],           # Дата занятия
                       'theme': j[Const.JRN_THEME],         # Тема занятия
                       'tstart': j[Const.JRN_START],         # Начало занятия
                       'tend': j[Const.JRN_END],             # Окончание занятия
                       'present': j[Const.JRN_PRESENT],     # Список присутствовавших
                       'estim': j[Const.JRN_ESTIM],         # Оценки
                       'shtraf': j[Const.JRN_SHTRAF],       # Штрафы
                       'comment': j[Const.JRN_COMMENT],     # Коментарии к занятию
                       'idGroups': j[Const.JRN_IDG]         # ID Уч.группы
                       }
                rec['count'] = len(rec['present'].split())
                gruppa = dict()
                for gt in filter(lambda x: x['idGroups'] == rec['idGroups'], self.d_g_table.values()):

                    present = 1 if gt['idUsers'] in map(int, rec['present'].split()) else 0
                    estim = {int(val.split('=')[0]): val.split('=')[1] for val in rec['estim'].split()}
                    shtraf = {int(val.split('=')[0]): val.split('=')[1] for val in rec['shtraf'].split()}

                    gruppa[gt['idUsers']] = {'name': gt['studname'], 'present': present,
                                             'estim': estim.get(gt['idUsers'], ''),
                                             'shtraf': shtraf.get(gt['idUsers'], '')}

                rec['users'] = gruppa
                self.d_groups[rec['idGroups']][j[Const.JRN_ID]] = rec
                self.d_journal[j[Const.JRN_ID]] = rec

            for g in self.d_groups.keys():
                self.full_struct[self.d_groups[g]['idCourses']]['grupps'][g] = self.d_groups[g]
            spis = []
            for key in self.full_struct.keys():
                if len(self.full_struct[key]['grupps']) == 0:
                    spis.append(key)
            for key in spis:
                self.full_struct.pop(key)

    def get_statistics(self):
        ret = {'year': Const.YEAR,                  # year      Учебный год
               'id': self.user_id,                  # id        ID Пользователя или None
               'cnt_usr': self.user.rows(),         # cnt_usr   Количество активных наставников
               'cnt_grp': self.groups.rows(),       # cnt_grp   Количество учебных групп
               'cnt_stud': self.g_table.rows(),     # cnt_stud  Количество кубистов в группах
               'cnt_week': self.rasp.rows(),        # cnt_week  Количество занятий в неделю
               'cnt_jrn': self.journal.rows()}      # cnt_jrn   Количество листов в журнале занятий
        dd_min = datetime.date.fromisoformat('2200-01-01')
        dd_max = datetime.date.fromisoformat('1900-01-01')
        if self.journal.rows() > 0:
            for dd in self.journal.data:
                dd_min = min(datetime.date.fromisoformat(dd[Const.JRN_DATE]), dd_min)
                dd_max = max(datetime.date.fromisoformat(dd[Const.JRN_DATE]), dd_max)
        else:
            dd_min = ''
            dd_max = ''
        ret['date_min'] = dd_min                    # date_min  Начальная дата журнала
        ret['date_max'] = dd_max                    # date_max  Конечная дата журнала
        if self.rasp.rows() > 0:
            ret['h_to_week'] = sum([n['countless'] for n in self.d_rasp.values()])
        else:
            ret['h_to_week'] = 0
        return ret

    def get_full_structure(self):
        return self.full_struct

# --------------------------
class StatModel(QAbstractTableModel):
    refresh_visual = pyqtSignal()

    def __init__(self, dict_obj: dict):
        super(StatModel, self).__init__()
        self.dict_obj = dict_obj
        self.sort_col = None

    def headerData(self, section: int, orientation: Qt.Orientation, role=None):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.sql_obj.header[section]
            else:
                return ''
        if role == Qt.BackgroundColorRole: # BackgroundRole:
            # See below for the data structure.
            return QtGui.QColor('#c0f0f0')
        if role == Qt.InitialSortOrderRole:
            self.beginResetModel()
            if self.sort_col == section:
                self.sql_obj.data.sort(key=lambda i: i[section], reverse=True)
                self.sort_col = -1
            else:
                self.sql_obj.data.sort(key=lambda i: i[section])
                self.sort_col = section
            self.endResetModel()
            return

    def columnCount(self, parent=None):
        if len(self.sql_obj.data) == 0:
            return 0
        else:
            return len(self.sql_obj.data[0])

    def rowCount(self, parent=None):
        return self.sql_obj.rows()

    def data(self, index: QModelIndex, role=None):
        ret = None
        if self.sql_obj.rows() > 0:
            row = index.row()
            col = index.column()
            if col in [Const.JRN_PRESENT, Const.JRN_ESTIM, Const.JRN_SHTRAF]:
                ret = len(self.sql_obj.data[row][col].split())
            else:
                ret = self.sql_obj.data[row][col]
                if isinstance(ret, str):
                    ret = ret.strip()
            if col in self.date_col:
                ret = date_us_ru(ret)
        else:
            ret = ' '
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if ret is None:
                return ""
            else:
                return str(ret)
        if role == Qt.TextAlignmentRole:
            if isinstance(ret, int) or isinstance(ret, float):
                # Align right, vertical middle.
                return Qt.AlignVCenter + Qt.AlignRight
        if role == Qt.BackgroundRole and index.row() % 2:
            # See below for the data structure.
            return QtGui.QColor('#f0fcfc')

    def flags(self, index):
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def endResetModel(self) -> None:
        self.refresh_visual.emit()
# --------------------------

if __name__ == '__main__':
    flog = LogWriter(fname='teachLog.txt')
    sys.excepthook = except_hook
    con = sqlite3.connect('../db/database_J.db')

    stat = Statistics(con, 19)
    print(stat.get_statistics())
    # print(stat.user.rows(), stat.d_user)
    # print(stat.groups.rows(), stat.d_groups)
    # print(stat.d_rasp)
    # pprint(stat.full_struct)
    # pprint(stat.d_groups)
