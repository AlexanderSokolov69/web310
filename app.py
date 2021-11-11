import datetime
from flask import g

from flask import Flask, render_template, request, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import extract
from werkzeug.utils import redirect
from data import db_session
from data.cl_const import Const
from data.db_class_access import access_action
from data.db_class_courses import Courses
from data.db_class_group_table import GroupTable
from data.db_class_groups import Groups
from data.db_class_journals import Journals
from data.db_class_priv import Priv
from data.db_class_rasp import Rasp
from data.db_class_roles import Roles
from data.db_class_users import Users
from data.misc import MyDict, date_us_ru, date_ru_us, journ_fill_month, journ_clear_month, Checker
from data.mod_stat import Statistics
from forms.f_journ import JournFilterForm
from forms.f_list_journ import ListFilterForm
from forms.f_new_rasp import NewRasp
from forms.f_rasp import RaspFilterForm
from forms.f_user import LoginForm, RegisterForm


app = Flask(__name__)
app.config['SECRET_KEY'] = 'AlexFalcon_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
db_session.global_init("DSN=it-cube64")


@app.before_request
def before_request():
    g.db_sess = db_session.create_session()
    g.YEAR = Const.YEAR
    # access_action(sel='TEST: Регистрация SQL сессии')


@app.teardown_request
def teardown_request(exception):
    g.db_sess.close()


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
    try:
        ret = g.db_sess.query(Users).get(user_id)
        access_action(idUser=ret.id, sel=f"Регистация в системе: {ret.name}")
    except Exception:
        ret = None
        flash(f"Ошибка обработки SQL", category='error')
    return ret


@app.route('/rasp/add/<int:id_rec>', methods=['GET', 'POST'])
@login_required
def rasp_add(id_rec):
    curr = g.db_sess.query(Rasp).get(id_rec)
    form = NewRasp(idGroups=curr.idGroups, idKabs=curr.idKabs, idDays=curr.idDays, tstart=curr.tstart,
                   tend=curr.tend, name='Новая', comment='')
    if form.validate_on_submit():
        if form.bb_submit.data:
            curr = g.db_sess.query(Rasp).get(id_rec)
            rasp = Rasp()
            rasp.idGroups = form.idGroups.raw_data[0]
            rasp.idKabs = form.idKabs.raw_data[0]
            rasp.idDays = form.idDays.raw_data[0]
            rasp.tstart = form.tstart.raw_data[0]
            rasp.tend = form.tend.raw_data[0]
            rasp.name = form.name.raw_data[0]
            rasp.comment = form.comment.raw_data[0]
            g.db_sess.add(rasp)
            g.db_sess.commit()
            flash('Запись добавлена', category='success')
        return redirect("/journ")
    return render_template("rasp_add.html", form=form)


@app.route('/rasp/delete/<int:id_rec>', methods=['GET'])
@login_required
def rasp_delete(id_rec):
    if rasp := g.db_sess.query(Rasp).get(id_rec):
        g.db_sess.delete(rasp)
        g.db_sess.commit()
        flash('Запись удалена', category='success')
    return redirect("/journ")


@app.route('/journ/add/<int:id_rec>', methods=['GET'])
@login_required
def jorn_add(id_rec):
    curr = g.db_sess.query(Journals).get(id_rec)
    journ = Journals()
    journ.date = curr.date
    journ.idGroups = curr.idGroups
    journ.tstart = curr.tstart
    journ.tend = curr.tend
    journ.name = curr.name
    g.db_sess.add(journ)
    g.db_sess.commit()
    flash('Запись добавлена', category='success')
    return redirect("/journ")


@app.route('/journ/edit/<int:id_rec>', methods=['POST', 'GET'])
@login_required
def jorn_edit(id_rec):
    current = g.db_sess.query(Journals).get(id_rec)
    groupname = f"{current.groups.name.strip()} {current.groups.comment}"
    form = ListFilterForm(current)
    if form.validate_on_submit():
        if form.sb_submit.data and Checker(True).time(form.fh_tstart.raw_data[0]). \
                time(form.fh_tend.raw_data[0]).date_ru(form.fh_date.raw_data[0]).flag:
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
            if current := g.db_sess.query(Journals).get(form.hide_id):
                current.date = date_ru_us(form.fh_date.raw_data[0])
                current.tstart = form.fh_tstart.raw_data[0]
                current.tend = form.fh_tend.raw_data[0]
                current.name = form.fh_theme.raw_data[0].strip()
                current.present = ' '.join(present)
                current.estim = ' '.join(estim)
                current.shtraf = ' '.join(shtraf)
                current.usercomm = ' '.join(usercomm)
                current.comment = form.fh_comment.raw_data[0].strip()
                g.db_sess.commit()
            else:
                flash(f"Ошибка обработки SQL", category='error')
        return redirect("/journ")
    return render_template("list_edit.html", form=form, groupname=groupname)


@app.route('/journ/delete/<int:id_rec>', methods=['GET'])
@login_required
def jorn_delete(id_rec):
    if journ := g.db_sess.query(Journals).get(id_rec):
        if not (journ.name and len(journ.name.strip()) > 8):
            try:
                if len(journ.present.split()) == 0:
                    raise IndexError
                else:
                    flash('Лист не пустой', category='error')
            except Exception:
                try:
                    g.db_sess.delete(journ)
                    g.db_sess.commit()
                    flash('Лист журнала удалён.', category='success')
                except Exception:
                    flash('[SQL] Ошибка удаления', category='error')
        else:
            flash('Заполнена тема занятия', category='error')
    return redirect("/journ")


@app.route('/journ', methods=['GET', 'POST'])
@login_required
def journ_view():
    form = JournFilterForm()
    dat = form.rasp
    cnt = dat.count()
    journ = []
    fjourn = g.db_sess.query(Journals).join(Groups).join(Courses). \
        filter(Groups.idUsers == current_user.id, Courses.year == Const.YEAR). \
        order_by(Journals.date, Journals.tstart)
    if form.ff_groups.data != 0:
        dat = dat.filter(Groups.id == form.ff_groups.data)
        fjourn = fjourn.filter(Groups.id == form.ff_groups.data)
    if form.ff_month.data != 0:
        fjourn = fjourn.filter(extract('month', Journals.date) == form.ff_month.data)
    for rec in fjourn:
        new = MyDict()
        new = MyDict(id=rec.id, date=date_us_ru(rec.date), tstart=rec.tstart, tend=rec.tend,
                     counter=0 if not rec.present else len(rec.present.split()),
                     name='' if not rec.name else rec.name.strip(),
                     comment='' if not rec.comment else rec.comment.strip(),
                     gruppa=f"{'' if not rec.groups.name else rec.groups.name.strip()} "
                            f"{'' if not rec.groups.comment else rec.groups.comment.strip()}")
        journ.append(new)
    if form.validate_on_submit():
        if form.submit.data:
            session['ff_groups'] = form.ff_groups.data
            session['ff_month'] = form.ff_month.data
        elif form.fill_add.data:
            journ_fill_month(month=form.ff_month.data, idGroups=form.ff_groups.data, rasp=dat, journ=journ)
            return redirect('/journ')
        elif form.fill_del.data:
            journ_clear_month(journ=journ)
            return redirect('/journ')
    return render_template("journ_view.html", form=form, spis=dat, journ=journ, cnt=cnt)


@app.route('/', methods=['GET', 'POST'])
def base():
    if current_user and current_user.is_authenticated:
        return redirect('/journ')
    else:
        return redirect('/main')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = g.db_sess.query(Users).join(Roles).join(Priv).filter(Users.login == form.login.data).first()
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
def index():
    try:
        rsp = g.db_sess.query(Rasp).join(Groups).join(Users).order_by(Rasp.idDays, Rasp.tstart, Rasp.idKabs)
        if not rsp:
            raise EOFError
        form_rasp = RaspFilterForm()
        dat = rsp
        if request.method == 'POST' and form_rasp.validate_on_submit():
            session['fr_users'] = form_rasp.fr_users.data
            session['fr_weekday'] = form_rasp.fr_weekday.data
            session['fr_kabinet'] = form_rasp.fr_kabinet.data
            session['fr_course'] = form_rasp.fr_course.data
            session['fr_group'] = form_rasp.fr_group.data
        if form_rasp.fr_users.data != 0:
            dat = dat.filter(Groups.idUsers == form_rasp.fr_users.data)
        if form_rasp.fr_weekday.data != 0:
            dat = dat.filter(Rasp.idDays == form_rasp.fr_weekday.data)
        if form_rasp.fr_kabinet.data != 0:
            dat = dat.filter(Rasp.idKabs == form_rasp.fr_kabinet.data)
        if form_rasp.fr_course.data != 0:
            dat = dat.filter(Groups.idCourses == form_rasp.fr_course.data)
        uslist = None
        if form_rasp.fr_group.data != 0:
            dat = dat.filter(Groups.id == form_rasp.fr_group.data)
            #
            # Формирование списков кубистов
            users = g.db_sess.query(Users).join(GroupTable).\
                filter(GroupTable.idGroups == form_rasp.fr_group.data).order_by(Users.ima)
            mystat = Statistics(users=users,
                                idGroups=form_rasp.fr_group.data,
                                date_to=datetime.date.today().isoformat())
            uslist = mystat.get_pres_stat()
        cnt = dat.count()
    except Exception:
        cnt = 0
        dat = None
        form_rasp = None
        flash(f"Ошибка обработки SQL", category='error')
    return render_template("rasp_view.html", items=dat, form_rasp=form_rasp, cnt=cnt, uslist=uslist)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        if not g.db_sess.query(Users).filter(Users.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь не найден, регистрация запрещена!")
        if g.db_sess.query(Users).filter(Users.login == form.login.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой логин уже есть в системе!")
        user = g.db_sess.query(Users).filter(Users.name == form.name.data).first()
        user.set_password(form.password.data, form.login.data)
        g.db_sess.commit()
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


@app.route("/rasp_free", methods=['GET', 'POST'])
def index_free():
    rsp = g.db_sess.query(Rasp).join(Groups).join(Users).order_by(Rasp.idDays, Rasp.tstart, Rasp.idKabs)
    form_rasp = RaspFilterForm()
    dat = rsp
    if request.method == 'POST' and form_rasp.validate_on_submit():
        session['fr_users'] = form_rasp.fr_users.data
        session['fr_weekday'] = form_rasp.fr_weekday.data
        session['fr_kabinet'] = form_rasp.fr_kabinet.data
        session['fr_course'] = form_rasp.fr_course.data
    if form_rasp.fr_users.data != 0:
        dat = dat.filter(Groups.idUsers == form_rasp.fr_users.data)
    if form_rasp.fr_weekday.data != 0:
        dat = dat.filter(Rasp.idDays == form_rasp.fr_weekday.data)
    if form_rasp.fr_kabinet.data != 0:
        dat = dat.filter(Rasp.idKabs == form_rasp.fr_kabinet.data)
    if form_rasp.fr_course.data != 0:
        dat = dat.filter(Groups.idCourses == form_rasp.fr_course.data)
    cnt = dat.count()
    return render_template("rasp_view_free.html", items=dat, form_rasp=form_rasp, cnt=cnt)


if __name__ == '__main__':
#    app.run(host='0.0.0.0')
    app.run(debug=True)
