import pyodbc
import datetime
from flask import Flask, render_template, request, make_response, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from sqlalchemy import extract
from werkzeug.utils import redirect
from wtforms import SubmitField, BooleanField, IntegerField

from data import db_session
from data.cl_const import Const
from data.db_class_courses import Courses
from data.db_class_days import Days
from data.db_class_groups import Groups
from data.db_class_journals import Journals
from data.db_class_kabs import Kabs
from data.db_class_priv import Priv
from data.db_class_rasp import Rasp
from data.db_class_roles import Roles
from data.db_class_users import Users
from data.misc import MyDict, date_us_ru, date_ru_us
from forms.f_journ import JournFilterForm
from forms.f_list_journ import ListFilterForm
from forms.f_rasp import RaspFilterForm
from forms.f_user import LoginForm, RegisterForm


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@app.teardown_appcontext
def shutdown_session(exception=None):
    pass
    # print(exception)
#    db_session.orm.close_all_sessions()


@app.errorhandler(404)
@app.errorhandler(401)
def not_found(error):
    msg = 'Ошибка'
    if "401" in str(error):
        msg = 'Пользователь не авторизован (401)'
    elif "404" in str(error):
        msg = 'Страница не найдена (404)'
    return render_template("error404.html", message=msg)


@login_manager.user_loader
def load_user(user_id):
    with db_session.create_session() as db_sess:
        ret = db_sess.query(Users).get(user_id)
    return ret


@app.route('/journ/add/<int:id_rec>', methods=['GET'])
@login_required
def jorn_add(id_rec):
    with db_session.create_session() as db_sess:
        curr = db_sess.query(Journals).get(id_rec)
        journ = Journals()
        journ.date = curr.date
        journ.idGroups = curr.idGroups
        journ.tstart = curr.tstart
        journ.tend = curr.tend
        journ.name = curr.name
        db_sess.add(journ)
        db_sess.commit()
    return redirect("/journ")


@app.route('/journ/edit/<int:id_rec>', methods=['POST', 'GET'])
@login_required
def jorn_edit(id_rec):
    with db_session.create_session() as db_sess:
        current = db_sess.query(Journals).get(id_rec)
    form = ListFilterForm(current)
#    for rec in form.fs_spisok:
#        print(rec)
    if form.validate_on_submit():
        if form.sb_submit.data:
            present = []
            estim = []
            shtraf = []
            usercomm = []
            for rec in form.fs_spisok.data['items']:
                if rec['present']:
                    present.append(str(rec['item_id']))
                if rec['estim']:
                    estim.append(f"{rec['item_id']}={rec['estim'].strip()}")
                if rec['shtraf']:
                    shtraf.append(f"{rec['item_id']}={rec['shtraf'].strip()}")
                if rec['comment']:
                    usercomm.append(f"{rec['item_id']}={rec['comment'].strip()}")
            # print(form.hide_id, form.fh_theme.data.strip(), date_ru_us(form.fh_date.data), form.fh_tstart.data,
            #       form.fh_tend.data, form.fh_comment.data.strip())
            # print(present, estim, shtraf, usercomm)
            with db_session.create_session() as db_sess:
                current = db_sess.query(Journals).get(form.hide_id)
                if current:
                    current.date = date_ru_us(form.fh_date.raw_data[0])
                    current.tstart = form.fh_tstart.raw_data[0]
                    current.tend = form.fh_tend.raw_data[0]
                    current.name = form.fh_theme.raw_data[0].strip()
                    current.present = ' '.join(present)
                    current.estim = ' '.join(estim)
                    current.shtraf = ' '.join(shtraf)
                    current.usercomm = ' '.join(usercomm)
                    current.comment = form.fh_comment.raw_data[0].strip()
                    db_sess.commit()
        return redirect("/journ")
    return render_template("list_edit.html", form=form)


@app.route('/journ/delete/<int:id_rec>', methods=['GET'])
@login_required
def jorn_delete(id_rec):
    with db_session.create_session() as db_sess:
        journ = db_sess.query(Journals).get(id_rec)
        if not(journ.name and len(journ.name.strip()) > 8):
            db_sess.delete(journ)
            db_sess.commit()
    return redirect("/journ")


@app.route('/journ', methods=['GET', 'POST'])
@login_required
def journ_view():
    form = JournFilterForm()
    dat = form.rasp
    with db_session.create_session() as db_sess:
        fjourn = db_sess.query(Journals).join(Groups).join(Courses).\
            filter(Groups.idUsers == current_user.id, Courses.year == Const.YEAR).\
            order_by(Journals.date, Journals.tstart)
        if form.validate_on_submit():
            session['ff_groups'] = form.ff_groups.data
            session['ff_month'] = form.ff_month.data
        if form.ff_groups.data != 0:
            dat = dat.filter(Groups.id == form.ff_groups.data)
            fjourn = fjourn.filter(Groups.id == form.ff_groups.data)
        if form.ff_month.data != 0:
            fjourn = fjourn.filter(extract('month', Journals.date) == form.ff_month.data)
        journ = []
        for rec in fjourn:
            new = MyDict()
            new = MyDict(id=rec.id, date=date_us_ru(rec.date), tstart=rec.tstart, tend=rec.tend,
                         counter=0 if not rec.present else len(rec.present.split()),
                         name='' if not rec.name else rec.name.strip(),
                         comment='' if not rec.comment else rec.comment.strip(),
                         gruppa=f"{'' if not rec.groups.name else rec.groups.name.strip()} "
                                f"{'' if not rec.groups.comment else rec.groups.comment.strip()}")
            journ.append(new)
    return render_template("journ_view.html", form=form, spis=dat, journ=journ)


@app.route('/rasp', methods=['GET', 'POST'])
@login_required
def free_view():
    with db_session.create_session() as db_sess:
        rsp = db_sess.query(Rasp).join(Groups).join(Users).order_by(Rasp.idDays, Rasp.tstart, Rasp.idKabs)
    form = RaspFilterForm()
    dat = rsp
    if form.validate_on_submit():
        #    if request.method == 'POST':
        if form.fr_users.data != 0:
            dat = dat.filter(Groups.idUsers == form.fr_users.data)
        if form.fr_weekday.data != 0:
            dat = dat.filter(Rasp.idDays == form.fr_weekday.data)
        if form.fr_kabinet.data != 0:
            dat = dat.filter(Rasp.idKabs == form.fr_kabinet.data)
        if form.fr_course.data != 0:
            dat = dat.filter(Groups.idCourses == form.fr_course.data)
    cnt = dat.count()
    return render_template("rasp_view_free.html", items=dat, form=form, cnt=cnt)


@app.route('/', methods=['GET', 'POST'])
def base():
    return render_template("empty.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        with db_session.create_session() as db_sess:
            user = db_sess.query(Users).join(Roles).join(Priv).filter(Users.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            session.current_user = user
            current_user.year = Const.YEAR
            return redirect("/journ")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/main", methods=['GET', 'POST'])
@login_required
def index():
    #    if request.method == 'GET':
    with db_session.create_session() as db_sess:
        rsp = db_sess.query(Rasp).join(Groups).join(Users).order_by(Rasp.idDays, Rasp.tstart, Rasp.idKabs)
    form_rasp = RaspFilterForm()
    dat = rsp
    if  request.method == 'POST' and form_rasp.validate_on_submit():
        session['fr_users'] = form_rasp.fr_users.data
        session['fr_weekday'] = form_rasp.fr_weekday.data
        session['fr_kabinet'] = form_rasp.fr_kabinet.data
        session['fr_course'] = form_rasp.fr_course.data
        #    if request.method == 'POST':
    if form_rasp.fr_users.data != 0:
        dat = dat.filter(Groups.idUsers == form_rasp.fr_users.data)
    if form_rasp.fr_weekday.data != 0:
        dat = dat.filter(Rasp.idDays == form_rasp.fr_weekday.data)
    if form_rasp.fr_kabinet.data != 0:
        dat = dat.filter(Rasp.idKabs == form_rasp.fr_kabinet.data)
    if form_rasp.fr_course.data != 0:
        dat = dat.filter(Groups.idCourses == form_rasp.fr_course.data)
    # print('goto /main')
    return render_template("rasp_view.html", items=dat, form_rasp=form_rasp)


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
    return redirect("/login")


@app.route('/base')
def base_view():
    return render_template('empty.html')


@app.route("/rasp")
def rasp_view():
    with db_session.create_session() as db_sess:
        rsp = db_sess.query(Rasp).order_by(Rasp.idDays, Rasp.tstart, Rasp.idKabs).all()
    return render_template("rasp_view_free.html", items=rsp)


def main():
    db_session.global_init("DSN=it-cube64")
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    main()
