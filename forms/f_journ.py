from flask import session
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField

from data import db_session
from data.cl_const import Const
from data.db_class_courses import Courses
from data.db_class_days import Days
from data.db_class_groups import Groups
from data.db_class_journals import Journals
from data.db_class_kabs import Kabs
from data.db_class_monts import Monts
from data.db_class_rasp import Rasp
from data.db_class_users import Users


class JournFilterForm(FlaskForm):
    ff_groups = SelectField(u'Учебная группа', coerce=int)
    ff_month = SelectField(u'Месяц', coerce=int)
    submit = SubmitField('Применить фильтр')
    fill_add = SubmitField('Заполнить')
    fill_del = SubmitField('Очистить')

    def __init__(self, *args, **kwargs):
        super(JournFilterForm, self).__init__(*args, **kwargs)
        with db_session.create_session() as db_sess:
            # Groups
            group = db_sess.query(Groups).join(Courses).\
                filter(Groups.idUsers == current_user.id, Courses.year == Const.YEAR).order_by(Groups.name)
            self.ff_groups.choices = [(g.id, u"%s" % f'{g.name}') for g in group]
            self.ff_groups.choices.insert(0, (0, u"Не выбрана"))
            if self.ff_groups.data is not None:
                self.ff_groups.default = self.ff_groups.data
            else:
                self.ff_groups.data = session.get('ff_groups', 0)
            # Месяц
            month = db_sess.query(Monts).order_by(Monts.id).all()
            self.ff_month.choices = [(g.num, u"%s" % f'{g.name}') for g in month]
            self.ff_month.choices.insert(0, (0, u"Не выбран"))
            if self.ff_month.data is not None:
                self.ff_month.default = self.ff_month.data
            else:
                self.ff_month.data = session.get('ff_month', 0)
            # Расписание занятий
            self.rasp = db_sess.query(Rasp).join(Groups).join(Days).join(Kabs). \
                filter(Groups.idUsers == current_user.id).order_by(Groups.name, Rasp.idDays)
            self.fill_flag = all([self.ff_groups.data, self.ff_month.data])

