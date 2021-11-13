import datetime

from flask import session, flash
from flask import g
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, BooleanField, SelectField, FieldList, DateField
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


class StatFilterForm(FlaskForm):
    fr_bdate = DateField(u'Начало периода', format='%d.%m.%Y',
                         default=datetime.date.fromisoformat(f"{Const.YEAR}-{Const.DATE_FROM}"),
                         validators=[DataRequired()])
    fr_edate = DateField(u'Окончание периода', format='%d.%m.%Y',default=datetime.date.today(), validators=[DataRequired()])
    fr_select = SelectField(u'Группировка статистики', coerce=int)
    fr_course = SelectField(u'Учебный курс', coerce=int)
    fr_users = SelectField(u'ФИО Наставника', coerce=int)
    submit = SubmitField('Сформировать')

    def __init__(self, *args, **kwargs):
        super(StatFilterForm, self).__init__(*args, **kwargs)
        spis = [(0, 'В целом по it-кубу'),
                (1, 'По наставникам'),
                (2, 'По учебным программам'),
                (3, 'По группам')
                ]
        self.fr_select.choices = spis
        self.fr_select.default = 0

        users = g.db_sess.query(Users).join(Roles).join(Priv).join(Groups, Groups.idUsers == Users.id). \
            join(Courses, Courses.id == Groups.idCourses). \
            filter(Priv.access.like(Const.ACC_PREPOD)).order_by(Users.name)
        # users = users.filter(Groups.id == self.fr_group.data)
        self.fr_users.choices = [(g.id, u"%s" % f'{g.name}') for g in users]
        self.fr_users.choices.insert(0, (0, u"Не выбрана"))

        courses = g.db_sess.query(Courses).join(Groups, Groups.idCourses == Courses.id). \
            order_by(Courses.name).filter(Courses.year == Const.YEAR)
        self.fr_course.choices = [(g.id, u"%s" % f'{g.name[:40:1]}') for g in courses]
        self.fr_course.choices.insert(0, (0, u"Не выбран"))
