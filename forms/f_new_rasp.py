from flask import session, flash
from flask import g
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, BooleanField, SelectField, FieldList

from data import db_session
from data.cl_const import Const
from data.db_class_courses import Courses
from data.db_class_days import Days
from data.db_class_groups import Groups
from data.db_class_kabs import Kabs


class NewRasp(FlaskForm):
    idGroups = SelectField(u'Учебная группа:', coerce=int)
    idKabs = SelectField(u'Кабинет:', coerce=int)
    idDays = SelectField(u'День недели:', coerce=int)
    tstart = StringField(u'Начало:')
    tend = StringField(u'Окончание:')
    name = StringField(u'Наименование:')
    comment = StringField(u'Доп.информация:')
    bb_submit = SubmitField(u'Сохранить')
    bb_cancel = SubmitField(u'Отменить')

    def __init__(self, *args, **kwargs):
        super(NewRasp, self).__init__(*args, **kwargs)
        # try:
        # with db_session.create_session() as db_sess:
        #     try:
        grps = g.db_sess.query(Groups).join(Courses).\
            filter(Groups.idUsers == current_user.id, Courses.year == Const.YEAR).\
            order_by(Groups.name)
        # except Exception as err:
        #     grps = None
        #     flash(f"Ошибка обработки SQL", category='error')
        self.idGroups.choices = [(rec.id, rec.name) for rec in grps]
        self.idGroups.data = kwargs.get('idGroups', 0)
        # Кабинет
        try:
            kabs = g.db_sess.query(Kabs).order_by(Kabs.id)
        except Exception as err:
            kabs = None
            flash(f"Ошибка обработки SQL", category='error')
        self.idKabs.choices = [(gg.id, u"%s" % f'{gg.name}') for gg in kabs]
        self.idKabs.data = kwargs.get('idKabs', 0)
        # День недели
        try:
            week_day = g.db_sess.query(Days).order_by(Days.id)
        except Exception as err:
            week_day = None
            flash(f"Ошибка обработки SQL", category='error')
        self.idDays.choices = [(gg.id, u"%s" % f'{gg.name}') for gg in week_day]
        self.idDays.data = kwargs.get('idDays', 0)
        # except Exception as err:
        #     db_sess = None
        #     flash(f"Ошибка обработки SQL", category='error')
        self.tstart.data = kwargs.get('tstart', '')
        self.tend.data = kwargs.get('tend', '')
        self.name.data = kwargs.get('name', '')


