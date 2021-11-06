import pyodbc
from flask import Flask, render_template, request, make_response, session
from flask_login import LoginManager, login_user, logout_user, login_required
from werkzeug.utils import redirect

from data import db_session
from data.cl_const import Const
from data.cl_password import Password
from data.db_class_courses import Courses
from data.db_class_days import Days
from data.db_class_groups import Groups
from data.db_class_kabs import Kabs
from data.db_class_priv import Priv
from data.db_class_rasp import Rasp
from data.db_class_roles import Roles
from data.db_class_users import Users
from forms.f_user import LoginForm, RegisterForm
from flask_restful import reqparse, abort, Api, Resource


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    with db_session.create_session() as db_sess:
        ret = db_sess.query(Users).get(user_id)
    return ret


@app.route('/login', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        with db_session.create_session() as db_sess:
            user = db_sess.query(Users).filter(Users.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/base")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        with db_session.create_session() as db_sess:
            if not db_sess.query(Users).filter(Users.name == form.name.data).first():
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Пользователь не найден, регистрация запрещена!")
            if db_sess.query(Users).filter(Users.login == form.login.data).first():
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Такой логин уже есть в системе!")
            user = db_sess.query(Users).filter(Users.name == form.name.data).first()
            user.set_password(form.password.data, form.login.data)
            db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/base')
def base_view():
    return render_template('base.html')


@app.route("/main")
@login_required
def index():
    with db_session.create_session() as db_sess:
        rsp = db_sess.query(Rasp).order_by(Rasp.idDays, Rasp.tstart, Rasp.idKabs).all()
    return render_template("rasp_view.html", items=rsp)


@app.route("/rasp")
def rasp_view():
    with db_session.create_session() as db_sess:
        rsp = db_sess.query(Rasp).order_by(Rasp.idDays, Rasp.tstart, Rasp.idKabs).all()
    return render_template("rasp_view_free.html", items=rsp)


def main():
    db_session.global_init("DSN=it-cube64")
    app.run()


if __name__ == '__main__':
    main()

