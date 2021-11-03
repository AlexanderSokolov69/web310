from flask import Flask, render_template, redirect
from data import db_session
from data.users import User
from data.users import User
from data.items import Items
from data.loginform import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

@app.route('/')
@app.route('/index')
def index():
    user = "Ученик Яндекс.Лицея"
    return render_template('index.html', title='Домашняя страница',
                           username='Незнакомец')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect('/viewtable')
    return render_template('login.html', title='Авторизация', form=form)

@app.route('/viewtable')
def viewtable():
    db_sess = db_session.create_session()
    spis = db_sess.query(Items).all()
    return render_template("viewtable.html", items=spis)

def main():
    db_session.global_init("db/database.db")
    app.run()

if __name__ == '__main__':
    main()