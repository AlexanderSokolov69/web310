#from flask .ext.wtf import Form
from flask import Flask, render_template, session, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, SubmitField, widgets

SECRET_KEY = 'development'

app = Flask(__name__)
app.config.from_object(__name__)


class ChoiceObj(object):
    def __init__(self, name, choices):
        # this is needed so that BaseForm.process will accept the object for the named form,
        # and eventually it will end up in SelectMultipleField.process_data and get assigned
        # to .data
        setattr(self, name, choices)


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.TableWidget()
    option_widget = widgets.CheckboxInput()

    # uncomment to see how the process call passes through this object
    # def process_data(self, value):
    #     return super(MultiCheckboxField, self).process_data(value)


class ColorLookupForm(FlaskForm):
    submit = SubmitField('Save')
    colors = MultiCheckboxField(None)


allColors = ( 'red', 'pink', 'blue', 'green', 'yellow', 'purple' )


@app.route('/', methods=['GET', 'POST'])
def color():
    selectedChoices = ChoiceObj('colors', session.get('selected') )
    form = ColorLookupForm(obj=selectedChoices)
    form.colors.choices =  [(c, c) for c in allColors]

    if form.validate_on_submit():
        session['selected'] = form.colors.data
        return redirect('/')
    else:
        print(form.errors)
    return render_template('color.html',
                           form=form,
                           selected=session.get('selected'))


if __name__ == '__main__':
    app.run()
