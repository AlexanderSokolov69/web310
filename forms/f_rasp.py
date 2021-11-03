from flask import session
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, BooleanField, SelectField, FieldList
from wtforms.validators import DataRequired

from data import db_session
from data.cl_const import Const
from data.db_class_courses import Courses
from data.db_class_days import Days
from data.db_class_kabs import Kabs
from data.db_class_priv import Priv
from data.db_class_roles import Roles
from data.db_class_users import Users


class RaspFilterForm(FlaskForm):
    f_users = SelectField(u'ФИО Наставника', coerce=int)
    f_weekday = SelectField(u'День недели', coerce=int)
    f_kabinet = SelectField(u'Кабинет', coerce=int)
    f_course = SelectField(u'Учебный курс', coerce=int)
    submit = SubmitField('Применить фильтр')

    def __init__(self, *args, **kwargs):
        super(RaspFilterForm, self).__init__(*args, **kwargs)
        db_sess = db_session.create_session()
        # Users
        users = db_sess.query(Users).join(Roles).join(Priv).filter(Priv.access.like(Const.ACC_PREPOD)).\
            order_by(Users.name).all()
        self.f_users.choices = [(g.id, u"%s" % f'{g.name}') for g in users]
        self.f_users.choices.insert(0, (0, u"Не выбрана"))
        self.f_users.default = session.get('f_users', 0)
        # День недели
        week_day = db_sess.query(Days).order_by(Days.id).all()
        self.f_weekday.choices = [(g.id, u"%s" % f'{g.name}') for g in week_day]
        self.f_weekday.choices.insert(0, (0, u"Не выбран"))
        self.f_weekday.default = session.get('f_weekday', 0)
        # Кабинет
        kabs = db_sess.query(Kabs).order_by(Kabs.id).all()
        self.f_kabinet.choices = [(g.id, u"%s" % f'{g.name}') for g in kabs]
        self.f_kabinet.choices.insert(0, (0, u"Не выбран"))
        self.f_kabinet.default = session.get('f_kabinet', 0)
        # Кабинет
        courses = db_sess.query(Courses).order_by(Courses.name).filter(Courses.year == Const.YEAR).all()
        self.f_course.choices = [(g.id, u"%s" % f'{g.name[:40:1]}') for g in courses]
        self.f_course.choices.insert(0, (0, u"Не выбран"))
        self.f_course.default = session.get('f_course', 0)
