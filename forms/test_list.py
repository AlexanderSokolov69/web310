from collections import namedtuple

from flask import session, flash
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

UserItem = namedtuple('UserItem', ['id', 'present', 'name'])

class UsersList(FlaskForm):
    id = IntegerField()
#    name = StringField(u'Фамилия И.О.')
    present = BooleanField()
    #shtraf = StringField(u'Штраф')

def create_list_users(spisok):
    class MyUsersList(UsersList):
        pass

    for user in spisok:
        setattr(MyUsersList, f'{user.id}')
        # setattr(MyUsersList, 'name', user.name)
        # setattr(MyUsersList, 'present', BooleanField(u'bool'))
    return MyUsersList()

class ListFilterForm(FlaskForm):
    fh_theme = TextAreaField(u'Тема занятия')
    fh_date = StringField(u'Дата')
    fh_tstart = StringField(u'Начало')
    fh_tend = StringField(u'Окончание')
    fh_comment = TextAreaField(u'Доп. комментарий')
    fs_spisok = FieldList(FormField(UsersList))
    fh_submit = SubmitField('Сохранить')
    fs_data = {}

    def __init__(self, current, *args, **kwargs):
        super(ListFilterForm, self).__init__(*args, **kwargs)
        self.fh_theme.data = current.name
        self.fh_date.data = date_us_ru(current.date)
        self.fh_tstart.data = current.tstart
        self.fh_tend.data = current.tend
        self.fh_comment.data = current.comment
        pres = [int(id) for id in current.present.split()]
        try:
            with db_session.create_session() as db_sess:
                try:
                    spis = db_sess.query(Users).join(GroupTable, GroupTable.idUsers == Users.id).\
                           filter(current.idGroups == GroupTable.idGroups).order_by(Users.name)
                except Exception as err:
                    spis = None
                    flash(f"Ошибка обработки SQL", category='error')
            for item_form in self.fs_spisok:
                for item in kwargs['data']['items']:
                    if item.id == item_form.item_id.data:
                        item_form.want.label =''
                        item_form.label = item.name
            users_list = []
            i = 1
            for user in spis:
                users_list.append(UserItem(i, user.id in pres, user.name))
                i += 1
            self.fs_data['items'] = users_list
        except Exception as err:
            db_sess = None
            flash(f"Ошибка обработки SQL", category='error')


