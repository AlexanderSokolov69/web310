from flask import session, flash
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
from data.db_session import executeSQL


class JournFilterForm(FlaskForm):
    ff_groups = SelectField(u'Учебная группа', coerce=int)
    ff_month = SelectField(u'Месяц', coerce=int)
    submit = SubmitField('Применить фильтр')
    fill_add = SubmitField('Заполнить')
    fill_del = SubmitField('Очистить')

    def __init__(self, *args, **kwargs):
        super(JournFilterForm, self).__init__(*args, **kwargs)
        try:
            with db_session.create_session() as db_sess:
                # group = executeSQL(f"""db_sess.query(Groups).join(Courses).\
                #     filter(Groups.idUsers == current_user.id, Courses.year == Const.YEAR).order_by(Groups.name)""")
                try:
                    group = db_sess.query(Groups).join(Courses).\
                        filter(Groups.idUsers == current_user.id, Courses.year == Const.YEAR).order_by(Groups.name)
                except Exception as err:
                    group = None
                    flash(f"Ошибка обработки SQL", category='error')
                self.ff_groups.choices = [(g.id, u"%s" % f'{g.name}') for g in group]
                self.ff_groups.choices.insert(0, (0, u"Не выбрана"))
                if self.ff_groups.data is not None:
                    self.ff_groups.default = self.ff_groups.data
                else:
                    self.ff_groups.data = session.get('ff_groups', 0)
                # Месяц
                try:
                    month = db_sess.query(Monts).order_by(Monts.id).all()
                except Exception as err:
                    month = None
                    flash(f"Ошибка обработки SQL", category='error')
                self.ff_month.choices = [(g.num, u"%s" % f'{g.name}') for g in month]
                self.ff_month.choices.insert(0, (0, u"Не выбран"))
                if self.ff_month.data is not None:
                    self.ff_month.default = self.ff_month.data
                else:
                    self.ff_month.data = session.get('ff_month', 0)
                # Расписание занятий
                try:
                    self.rasp = db_sess.query(Rasp).join(Groups).join(Days).join(Kabs). \
                        filter(Groups.idUsers == current_user.id).order_by(Groups.name, Rasp.idDays)
                except Exception as err:
                    self.rasp = None
                    flash(f"Ошибка обработки SQL", category='error')
                self.fill_flag = all([self.ff_groups.data, self.ff_month.data])
        except Exception as err:
            db_sess = None
            flash(f"Ошибка обработки SQL", category='error')

