from collections import namedtuple

from flask import session
from flask_login import current_user
from flask_wtf import FlaskForm, Form
from werkzeug.datastructures import MultiDict
from wtforms import SelectField, SubmitField, StringField, FieldList, \
    TextAreaField, BooleanField, IntegerField, FormField, HiddenField

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

UserItem = namedtuple('UserItem', ['item_id', 'fio', 'present', 'b', 'c', 'name'])


class UsersList(FlaskForm):
    item_id = IntegerField()
    fio = StringField()
    present = BooleanField()
    b = StringField()
    c = StringField()

    def __repr__(self):
        ret = super(UsersList, self).__repr__()
        print(ret)
        return ret

class UserListForm(Form):
    items = FieldList(FormField(UsersList))

    def __init__(self, *args, **kwargs):
        super(UserListForm, self).__init__(*args, **kwargs)
        for item_form in self.items:
            for item in kwargs['data']['items']:
                if item.item_id == item_form.data['item_id']:
                    item_form.present.label =''
                    # item_form['shtraf'].label = 'sht'
#                    item_form.label = item.item_id


class ListFilterForm(FlaskForm):
    fh_theme = TextAreaField(u'Тема занятия')
    fh_date = StringField(u'Дата')
    fh_tstart = StringField(u'Начало')
    fh_tend = StringField(u'Окончание')
    fh_comment = TextAreaField(u'Доп. комментарий')
    fs_spisok = None
    fh_submit = SubmitField('Сохранить')


    def __init__(self, current):
        super(ListFilterForm, self).__init__()
        self.fh_theme.data = current.name
        self.fh_date.data = date_us_ru(current.date)
        self.fh_tstart.data = current.tstart
        self.fh_tend.data = current.tend
        self.fh_comment.data = current.comment
        db_sess = db_session.create_session()
        pres = [int(id) for id in current.present.split()]
        spis = db_sess.query(Users).join(GroupTable, GroupTable.idUsers == Users.id).\
               filter(current.idGroups == GroupTable.idGroups).order_by(Users.name).all()

        users_list = []
        for user in spis:
            users_list.append(UserItem(user.id, user.name, user.id in pres, '', '', user.name))
        data = MyDict()
        data['items'] = users_list
#        print(data)
        self.fs_spisok = UserListForm(data=data)

 #       print(self.fs_spisok.items())


