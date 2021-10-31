from flask import session, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FieldList, IntegerField, FormField, \
    SelectField
from wtforms.validators import DataRequired
from . import db_session
from data.box import Box
from .class_type import Class_type
from .item_type import Item_type
from .place import Place


class ViewTableForm(FlaskForm):
    class_list = SelectField(u'Класс', coerce=int)
    class_plus = SubmitField('o')
    type_list = SelectField(u'Тип', coerce=int)
    type_plus = SubmitField('o')
    place_list = SelectField(u'Место', coerce=int)
    place_plus = SubmitField('o')
    box_list = SelectField(u'Кейс', coerce=int)
    box_plus = SubmitField('o')
    param_str = StringField(label='Параметр', default='')
    place_pos_str = StringField(label='Позиция', default='')
    comment_str = StringField(label='Описание', default='')
    submit = SubmitField('Применить фильтр')
    reset_flt = SubmitField('Сбросить фильтр')
    add_btn = SubmitField('Добавить объект')
    del_btn = SubmitField('Удалить')
    edit_btn = SubmitField('Сохранить')
    cancel_btn = SubmitField('Назад')

    def __init__(self, *args, **kwargs):
        super(ViewTableForm, self).__init__(*args, **kwargs)
        sess = db_session.create_session()
        # Class_type
        spis = sess.query(Class_type).order_by(Class_type.param, Class_type.name).all()
        self.class_list.choices = [(g.id, u"%s" % f'{g.name} [{g.param}]') for g in spis]
        self.class_list.choices.insert(0, (0, u"Не выбрана"))
#        session['class_type_id'] = session.get('class_type_id', 0)
        self.class_list.default = session.get('class_type_id', 0)
        # Item_type
        spis = sess.query(Item_type).order_by(Item_type.name).all()
        self.type_list.choices = [(g.id, u"%s" % f'{g.name} [{g.param}] {g.mult}') for g in spis]
        self.type_list.choices.insert(0, (0, u"Не выбрана"))
#        session['item_type_id'] = session.get('item_type_id', 0)
        self.type_list.default = session.get('item_type_id', 0)
        # Place
        spis = sess.query(Place).order_by(Place.name).all()
        self.place_list.choices = [(g.id, u"%s" % f'{g.name} [{g.param}]') for g in spis]
        self.place_list.choices.insert(0, (0, u"Не выбрана"))
#        session['place_id'] = session.get('place_id', 0)
        self.place_list.default = session.get('place_id', 0)
        # Box
        spis = sess.query(Box).order_by(Box.name).all()
        self.box_list.choices = [(g.id, u"%s" % f'{g.name} [{g.param}]') for g in spis]
        self.box_list.choices.insert(0, (0, u"Не выбрана"))
#        session['box_id'] = session.get('box_id', 0)
        self.box_list.default = session.get('box_id', 0)

    def refresh(self, class_id):
        sess = db_session.create_session()
        # Item_type
        spis = sess.query(Item_type).filter(Item_type.class_type_id == class_id).order_by(Item_type.name).all()
        self.type_list.choices = [(g.id, u"%s" % f'{g.name} [{g.param}] {g.mult}') for g in spis]
        self.type_list.choices.insert(0, (0, u"Не выбрана"))
        self.type_list.default = 0

    def setup(self):
        self.class_list.data = int(request.form.get('class_list', '0'))
        self.type_list.data = int(request.form.get('type_list', '0'))
        self.place_list.data = int(request.form.get('place_list', '0'))
        self.box_list.data = int(request.form.get('box_list', '0'))
