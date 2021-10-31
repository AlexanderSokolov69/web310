from flask_wtf import FlaskForm
from wtforms import SubmitField


class About(FlaskForm):
    about = ['Каталогизатор',
             'Программа предназначена для упорядочивания',
             'хранения различного хлама, которым неизбежно',
             'обрастает квартира, а домохозяйство - тем более..',
             'Автор.']
