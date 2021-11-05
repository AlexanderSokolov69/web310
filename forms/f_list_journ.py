from flask import session
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField, FieldList, \
    TextAreaField, BooleanField, IntegerField, FormField

from data import db_session
from data.cl_const import Const
from data.db_class_courses import Courses
from data.db_class_days import Days
from data.db_class_group_table import GroupTable
from data.db_class_groups import Groups
from data.db_class_journals import Journals
from data.db_class_kabs import Kabs
from data.db_class_monts import Monts
from data.db_class_rasp import Rasp
from data.db_class_users import Users
from data.misc import date_us_ru, MyDict

class UsersList(FlaskForm):
    id = IntegerField(u'ID')
    name = StringField(u'Фамилия И.О.')
    present = BooleanField(u'Посещ.')
    shtraf = StringField(u'Штраф')


class ListFilterForm(FlaskForm):
    fh_theme = TextAreaField(u'Тема занятия')
    fh_date = StringField(u'Дата')
    fh_tstart = StringField(u'Начало')
    fh_tend = StringField(u'Окончание')
    fh_comment = TextAreaField(u'Доп. комментарий')
    fs_spisok = FieldList(FormField(UsersList))
    fh_submit = SubmitField('Сохранить')

    def __init__(self, list, *args, **kwargs):
        super(ListFilterForm, self).__init__(*args, **kwargs)
        self.fh_theme.data = list.name
        self.fh_date.data = date_us_ru(list.date)
        self.fh_tstart.data = list.tstart
        self.fh_tend.data = list.tend
        self.fh_comment.data = list.comment
        db_sess = db_session.create_session()
        spis = db_sess.query(Users).join(GroupTable, GroupTable.idUsers == Users.id).\
            filter(list.idGroups == GroupTable.idGroups).order_by(Users.name)
        pres = [int(id) for id in list.present.split()]

        for user in spis:
            self.fs_spisok.append_entry()
            self.fs_spisok[-1].id = user.id
            self.fs_spisok[-1].name = user.name
            self.fs_spisok[-1].present.default = "checked" if user.id in pres else None
        
        

