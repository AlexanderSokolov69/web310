from flask import session, flash
from flask import g
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, BooleanField, SelectField, FieldList
from wtforms.validators import DataRequired

from data import db_session
from data.cl_const import Const
from data.db_class_courses import Courses
from data.db_class_days import Days
from data.db_class_groups import Groups
from data.db_class_kabs import Kabs
from data.db_class_priv import Priv
from data.db_class_roles import Roles
from data.db_class_users import Users


class RaspFilterForm(FlaskForm):
    fr_course = SelectField(u'Учебный курс', coerce=int)
    fr_group = SelectField(u'Учебная группа', coerce=int)
    fr_users = SelectField(u'ФИО Наставника', coerce=int)
    fr_weekday = SelectField(u'День недели', coerce=int)
    fr_kabinet = SelectField(u'Кабинет', coerce=int)
    submit = SubmitField('Применить фильтр')

    def __init__(self, *args, **kwargs):
        super(RaspFilterForm, self).__init__(*args, **kwargs)
        # try:
        # with db_session.create_session() as db_sess:
        #     # Users
        #     try:
        users = g.db_sess.query(Users).join(Roles).join(Priv).join(Groups, Groups.idUsers == Users.id).\
            join(Courses, Courses.id == Groups.idCourses).\
            filter(Priv.access.like(Const.ACC_PREPOD)).order_by(Users.name)
        if self.fr_course.data:
            users = users.filter(Courses.id == self.fr_course.data)
        if self.fr_group.data:
            users = users.filter(Groups.id == self.fr_group.data)
            # except Exception as err:
            #     users = None
            #     flash(f"Ошибка обработки SQL", category='error')
        self.fr_users.choices = [(g.id, u"%s" % f'{g.name}') for g in users]
        self.fr_users.choices.insert(0, (0, u"Не выбрана"))
        if self.fr_users.data is not None:
            self.fr_users.default = self.fr_users.data
        else:
            self.fr_users.data = session.get('fr_users', 0)
        # День недели
        try:
            week_day = g.db_sess.query(Days).order_by(Days.id)
        except Exception as err:
            week_day = None
            flash(f"Ошибка обработки SQL", category='error')
        self.fr_weekday.choices = [(gg.id, u"%s" % f'{gg.name}') for gg in week_day]
        self.fr_weekday.choices.insert(0, (0, u"Не выбран"))
        if self.fr_weekday.data is not None:
            self.fr_weekday.default = self.fr_weekday.data
        else:
            self.fr_weekday.data = session.get('fr_weekday', 0)
        # Кабинет
        try:
            kabs = g.db_sess.query(Kabs).order_by(Kabs.id)
        except Exception as err:
            kabs = None
            flash(f"Ошибка обработки SQL", category='error')
        self.fr_kabinet.choices = [(gg.id, u"%s" % f'{gg.name}') for gg in kabs]
        self.fr_kabinet.choices.insert(0, (0, u"Не выбран"))
        if self.fr_kabinet.data is not None:
            self.fr_kabinet.default = self.fr_kabinet.data
        else:
            self.fr_kabinet.data = session.get('fr_kabinet', 0)
        # Учебный курс
        try:
            courses = g.db_sess.query(Courses).join(Groups, Groups.idCourses == Courses.id).\
                order_by(Courses.name).filter(Courses.year == Const.YEAR)
            if self.fr_users.data:
                courses = courses.filter(Groups.idUsers == self.fr_users.data)
            if self.fr_group.data:
                courses = courses.filter(Groups.id == self.fr_group.data)
        except Exception as err:
            courses = None
            flash(f"Ошибка обработки SQL", category='error')
        self.fr_course.choices = [(g.id, u"%s" % f'{g.name[:40:1]}') for g in courses]
        self.fr_course.choices.insert(0, (0, u"Не выбран"))
        if self.fr_course.data is not None:
            self.fr_course.default = self.fr_course.data
        else:
            self.fr_course.data = session.get('fr_course', 0)
        # Учебная группа
        try:
            groups = g.db_sess.query(Groups).join(Courses).order_by(Groups.name).\
                filter(Courses.year == Const.YEAR)
            if  self.fr_course.data:
                groups = groups.filter( Courses.id == self.fr_course.data)
            if self.fr_users.data:
                groups = groups.filter(Groups.idUsers == self.fr_users.data)
        except Exception as err:
            groups = None
            flash(f"Ошибка обработки SQL", category='error')
        self.fr_group.choices = [(gg.id, u"%s" % f'{gg.name} {gg.comment}') for gg in groups]
        self.fr_group.choices.insert(0, (0, u"Не выбрана"))
        if self.fr_group.data is not None:
            self.fr_group.default = self.fr_group.data
        else:
            self.fr_group.data = session.get('fr_group', 0)
        # except Exception as err:
        #     db_sess = None
        #     flash(f"Ошибка обработки SQL", category='error')
