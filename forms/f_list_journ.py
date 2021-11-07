from collections import namedtuple

from flask import session
from flask_login import current_user
from flask_wtf import FlaskForm
from werkzeug.datastructures import MultiDict
from wtforms import SelectField, SubmitField, StringField, FieldList, \
    TextAreaField, BooleanField, IntegerField, FormField, HiddenField
from wtforms.validators import DataRequired

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
from data.misc import date_us_ru, MyDict, spis_to_dic
from flask_validator import Validator

UserItem = namedtuple('UserItem', ['item_id', 'fio', 'present', 'estim', 'shtraf',
                                   'comment', 'navigator', 'name'])


class UsersList(FlaskForm):
    item_id = HiddenField()
    fio = StringField()
    present = BooleanField()
    estim = StringField()
    shtraf = StringField()
    comment = StringField()
    navigator = BooleanField()


class UserListForm(FlaskForm):
    items = FieldList(FormField(UsersList))

    # def __init__(self, *args, **kwargs):
    #     super(UserListForm, self).__init__(*args, **kwargs)
#         for item_form in self.items:
#             for item in kwargs['data']['items']:
#                 if item.item_id == item_form.data['item_id']:
#                     item_form.present.label =''
#                     # item_form['shtraf'].label = 'sht'
# #                    item_form.label = item.item_id


class ListFilterForm(FlaskForm):
    hide_id = HiddenField()
    fh_theme = TextAreaField(u'Тема занятия')
    fh_date = StringField(u'Дата', validators=[DataRequired()])
    fh_tstart = StringField(u'Начало', validators=[DataRequired()])
    fh_tend = StringField(u'Окончание', validators=[DataRequired()])
    fh_comment = TextAreaField(u'Доп. комментарий')
    fs_spisok = None
    sb_submit = SubmitField('Сохранить')
    sb_cancel = SubmitField('Назад')

    def __init__(self, current):
        super(ListFilterForm, self).__init__()
        self.hide_id = current.id
        self.fh_theme.data = '' if not current.name else current.name.strip()
        self.fh_date.data = date_us_ru(current.date)
        self.fh_tstart.data = current.tstart
        self.fh_tend.data = current.tend
        self.fh_comment.data = '' if not current.comment else current.comment.strip()
        pres = [] if not current.present else [int(id) for id in current.present.split()]
        estim = spis_to_dic(current.estim)
        shtraf = spis_to_dic(current.shtraf)
        comment = spis_to_dic(current.usercomm)

        with db_session.create_session() as db_sess:
            spis = db_sess.query(Users).join(GroupTable, GroupTable.idUsers == Users.id).\
                   filter(current.idGroups == GroupTable.idGroups).order_by(Users.name).all()

        users_list = []
        for user in spis:
            _id = user.id
            users_list.append(UserItem(_id, user.name, _id in pres,estim[_id] ,shtraf[_id], comment[_id],
                                       '1' in user.navigator, user.name))
        data = MyDict()
        data['items'] = users_list
        self.fs_spisok = UserListForm(data=data)




