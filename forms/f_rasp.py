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
    fr_users = SelectField(u'ФИО Наставника', coerce=int)
    fr_weekday = SelectField(u'День недели', coerce=int)
    fr_kabinet = SelectField(u'Кабинет', coerce=int)
    fr_course = SelectField(u'Учебный курс', coerce=int)
    submit = SubmitField('Применить фильтр')

    def __init__(self, *args, **kwargs):
        super(RaspFilterForm, self).__init__(*args, **kwargs)
        with db_session.create_session() as db_sess:
            # Users
            users = db_sess.query(Users).join(Roles).join(Priv).filter(Priv.access.like(Const.ACC_PREPOD)).\
                order_by(Users.name).all()
            self.fr_users.choices = [(g.id, u"%s" % f'{g.name}') for g in users]
            self.fr_users.choices.insert(0, (0, u"Не выбрана"))
            if self.fr_users.data is not None:
                self.fr_users.default = self.fr_users.data
            else:
                self.fr_users.data = session.get('fr_users', 0)
            # День недели
            week_day = db_sess.query(Days).order_by(Days.id).all()
            self.fr_weekday.choices = [(g.id, u"%s" % f'{g.name}') for g in week_day]
            self.fr_weekday.choices.insert(0, (0, u"Не выбран"))
            if self.fr_weekday.data is not None:
                self.fr_weekday.default = self.fr_weekday.data
            else:
                self.fr_weekday.data = session.get('fr_weekday', 0)
            # Кабинет
            kabs = db_sess.query(Kabs).order_by(Kabs.id).all()
            self.fr_kabinet.choices = [(g.id, u"%s" % f'{g.name}') for g in kabs]
            self.fr_kabinet.choices.insert(0, (0, u"Не выбран"))
            if self.fr_kabinet.data is not None:
                self.fr_kabinet.default = self.fr_kabinet.data
            else:
                self.fr_kabinet.data = session.get('fr_kabinet', 0)
            # Кабинет
            courses = db_sess.query(Courses).order_by(Courses.name).filter(Courses.year == Const.YEAR).all()
            self.fr_course.choices = [(g.id, u"%s" % f'{g.name[:40:1]}') for g in courses]
            self.fr_course.choices.insert(0, (0, u"Не выбран"))
            if self.fr_course.data is not None:
                self.fr_course.default = self.fr_course.data
            else:
                self.fr_course.data = session.get('fr_course', 0)
