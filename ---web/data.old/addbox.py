from flask import session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField, FloatField
from wtforms.validators import DataRequired

from data import db_session
from data.box import Box
from data.class_type import Class_type
from data.item_type import Item_type
from data.place import Place


class AddBox(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    param = StringField('Описание', validators=[DataRequired()])
    add_btn = SubmitField('Добавить')
    del_btn = SubmitField('Удалить')
    edit_btn = SubmitField('Сохранить')

    def __init__(self, box_id=0, *args, **kwargs):
        super(AddBox, self).__init__(*args, **kwargs)
        sess = db_session.create_session()
        obj = sess.query(Box).filter(Box.id == box_id).first()
        if obj:
            self.box_id = obj.id
            self.name.data = obj.name
            self.param.data = obj.param
        else:
            self.box_id = 0


class AddPlace(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    param = StringField('Описание', validators=[DataRequired()])
    add_btn = SubmitField('Добавить')
    del_btn = SubmitField('Удалить')
    edit_btn = SubmitField('Сохранить')

    def __init__(self, box_id=0, *args, **kwargs):
        super(AddPlace, self).__init__(*args, **kwargs)
        sess = db_session.create_session()
        obj = sess.query(Place).filter(Place.id == box_id).first()
        if obj:
            self.place_id = obj.id
            self.name.data = obj.name
            self.param.data = obj.param
        else:
            self.place_id = 0


class AddClass(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    param = StringField('Описание', validators=[DataRequired()])
    add_btn = SubmitField('Добавить')
    del_btn = SubmitField('Удалить')
    edit_btn = SubmitField('Сохранить')

    def __init__(self, class_id=0, *args, **kwargs):
        super(AddClass, self).__init__(*args, **kwargs)
        sess = db_session.create_session()
        obj = sess.query(Class_type).filter(Class_type.id == class_id).first()
        if obj:
            self.class_id = obj.id
            self.name.data = obj.name
            self.param.data = obj.param
        else:
            self.class_id = 0


class AddType(FlaskForm):
    class_list = SelectField(u'Класс', coerce=int)
    name = StringField('Название', validators=[DataRequired()])
    param = StringField('Описание', validators=[DataRequired()])
    mult = FloatField('Множитель')
    add_btn = SubmitField('Добавить')
    del_btn = SubmitField('Удалить')
    edit_btn = SubmitField('Сохранить')

    def __init__(self, type_id=0, *args, **kwargs):
        super(AddType, self).__init__(*args, **kwargs)
        sess = db_session.create_session()
        obj = sess.query(Item_type).filter(Item_type.id == type_id).first()
        if obj:
            self.type_id = obj.id
            self.class_type_id = obj.class_type_id
            self.name.data = obj.name
            self.param.data = obj.param
            self.mult.data = obj.mult
        else:
            self.type_id = 0
        spis = sess.query(Class_type).order_by(Class_type.param, Class_type.name).all()
        self.class_list.choices = [(g.id, u"%s" % f'{g.name} [{g.param}]') for g in spis]
        self.class_list.choices.insert(0, (0, u"Не выбрана"))
#        session['class_type_id'] = session.get('class_type_id', 0)
        if obj:
            self.class_list.default = obj.class_type_id
