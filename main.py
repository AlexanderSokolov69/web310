from flask import Flask, render_template, redirect, session, make_response, jsonify, flash, request
from data import db_session, items_api
from data.about import About
from data.addbox import AddBox, AddPlace, AddClass, AddType
from data.box import Box
from data.class_type import Class_type
from data.item_type import Item_type
from data.place import Place
from data.users import User
from data.items import Items
from data.loginform import LoginForm, RegisterForm
from data.viewtableform import ViewTableForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/about')
def about():
    form = About()
    if form.validate_on_submit():
        pass
#        return redirect('/')
    return render_template('about.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def registeruser():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        test = db_sess.query(User).filter(User.name == request.form['name']).first()
        if test:
            flash('Такой пользователь уже есть')
        else:
            new_user = User(request.form['name'], request.form['fullname'], request.form['password1'])
            db_sess.add(new_user)
            db_sess.commit()
            return redirect('/login')
    return render_template('login.html', title='Регистрация', form=form, new_user=True)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.name == form.name.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/viewtable")
        flash('Неправильный логин или пароль')
    return render_template('login.html', title='Авторизация', form=form, new_user=False)


@app.route('/edit/box/<int:box_id>', methods=['GET', 'POST'])
@login_required
def editbox(box_id):
    box = AddBox(box_id)
    db_sess = db_session.create_session()
    spis = db_sess.query(Box).order_by(Box.name, Box.param).all()
    session['update_spis'] = True
    if box.validate_on_submit():
        if box.add_btn.data:
            obj = Box(request.form['name'], request.form['param'])
            db_sess.add(obj)
            db_sess.commit()
            return redirect("/edit/box/0")
        if box.edit_btn.data and box_id:
            test = db_sess.query(Box).filter(Box.id == box_id).first()
            test.name = request.form['name']
            test.param = request.form['param']
            db_sess.commit()
            return redirect(f"/edit/box/{box_id}")
        if box.del_btn.data and box_id:
            test = db_sess.query(Items).filter(Items.box_id == box_id).first()
            if test:
                flash('Невозможно. Есть связанные записи')
            else:
                test = db_sess.query(Box).filter(Box.id == box_id).delete()
                db_sess.commit()
                return redirect("/edit/box/0")
    return render_template("addbox.html", form=box, items=spis)


@app.route('/edit/place/<int:place_id>', methods=['GET', 'POST'])
@login_required
def editplace(place_id):
    box = AddPlace(place_id)
    db_sess = db_session.create_session()
    spis = db_sess.query(Place).order_by(Place.name, Place.param).all()
    session['update_spis'] = True
    if box.validate_on_submit():
        if box.add_btn.data:
            obj = Place(request.form['name'], request.form['param'])
            db_sess.add(obj)
            db_sess.commit()
            return redirect("/edit/place/0")
        if box.edit_btn.data and place_id:
            test = db_sess.query(Place).filter(Place.id == place_id).first()
            test.name = request.form['name']
            test.param = request.form['param']
            db_sess.commit()
            return redirect(f"/edit/place/{place_id}")
        if box.del_btn.data and place_id:
            test = db_sess.query(Items).filter(Items.place_id == place_id).first()
            if test:
                flash('Невозможно. Есть связанные записи')
            else:
                test = db_sess.query(Place).filter(Place.id == place_id).delete()
                db_sess.commit()
                return redirect("/edit/place/0")
    return render_template("addplace.html", form=box, items=spis)


@app.route('/edit/class/<int:class_id>', methods=['GET', 'POST'])
@login_required
def editclass(class_id):
    box = AddClass(class_id)
    db_sess = db_session.create_session()
    spis = db_sess.query(Class_type).order_by(Class_type.name, Class_type.param).all()
    session['update_spis'] = True
    if box.validate_on_submit():
        if box.add_btn.data:
            obj = Class_type(request.form['name'], request.form['param'])
            db_sess.add(obj)
            db_sess.commit()
            return redirect("/edit/class/0")
        if box.edit_btn.data and class_id:
            test = db_sess.query(Class_type).filter(Class_type.id == class_id).first()
            test.name = request.form['name']
            test.param = request.form['param']
            db_sess.commit()
            return redirect(f"/edit/class/{class_id}")
        if box.del_btn.data and class_id:
            test = db_sess.query(Item_type).filter(Item_type.class_type_id == class_id).first()
            if test:
                flash('Невозможно. Есть связанные записи')
            else:
                test = db_sess.query(Class_type).filter(Class_type.id == class_id).delete()
                db_sess.commit()
                return redirect("/edit/class/0")
    return render_template("addclass.html", form=box, items=spis)


@app.route('/edit/type/<int:type_id>', methods=['GET', 'POST'])
@login_required
def edittype(type_id):
    box = AddType(type_id)
    db_sess = db_session.create_session()
    spis = db_sess.query(Item_type).order_by(Item_type.name, Item_type.param).all()
    session['update_spis'] = True
    if box.validate_on_submit():
        if box.add_btn.data:
            if int(request.form.get('class_list', '0')):
                obj = Item_type(int(request.form.get('class_list', '0')), request.form['name'],
                                request.form['param'], float(request.form['mult']))
                db_sess.add(obj)
                db_sess.commit()
                return redirect("/edit/type/0")
            else:
                flash('Не выбран класс')
        if box.edit_btn.data and type_id:
            test = db_sess.query(Item_type).filter(Item_type.id == type_id).first()
            test.name = request.form['name']
            test.param = request.form['param']
            test.mult = float(request.form['mult'])
            db_sess.commit()
            return redirect(f"/edit/type/{type_id}")
        if box.del_btn.data and type_id:
            test = db_sess.query(Items).filter(Items.item_type_id == type_id).first()
            if test:
                flash('Невозможно. Есть связанные записи')
            else:
                test = db_sess.query(Item_type).filter(Item_type.id == type_id).delete()
                db_sess.commit()
                return redirect("/edit/type/0")
    if type_id:
        box.class_list.data = box.class_type_id
    else:
        box.class_list.data = session['class_type_id']
    return render_template("addtype.html", form=box, items=spis)


@app.route('/', methods=['GET', 'POST'])
@app.route('/viewtable', methods=['GET', 'POST'])
def viewtable():
    if current_user.is_authenticated:
        view_form = ViewTableForm()
        db_sess = db_session.create_session()
        spis = db_sess.query(Items)
        if view_form.class_plus.data:
            return redirect(f'/edit/class/{request.form["class_list"]}')
        if view_form.type_plus.data:
            session['class_type_id'] = request.form['class_list']
            return redirect(f'/edit/type/{request.form["type_list"]}')
        if view_form.place_plus.data:
            return redirect(f'/edit/place/{request.form["place_list"]}')
        if view_form.box_plus.data:
            return redirect(f'/edit/box/{request.form["box_list"]}')
        if view_form.validate_on_submit():
            if view_form.add_btn.data:
                session['class_type_id'] = int(request.form['class_list'])
                session['item_type_id'] = int(request.form['type_list'])
                session['place_id'] = int(request.form['place_list'])
                session['box_id'] = int(request.form['box_list'])
                return redirect('/viewitem/0')
            if view_form.submit.data:
                session['class_type_id'] = int(request.form['class_list'])
                session['item_type_id'] = int(request.form['type_list'])
                session['place_id'] = int(request.form['place_list'])
                session['box_id'] = int(request.form['box_list'])
                test = False
                if int(request.form['class_list']):
                    view_form.refresh(int(request.form['class_list']))
                if int(request.form['type_list']):
                    test = True
                    spis = spis.filter(Items.item_type_id == int(request.form['type_list']))
                if int(request.form['place_list']):
                    test = True
                    spis = spis.filter(Items.place_id == int(request.form['place_list']))
                if int(request.form['box_list']):
                    test = True
                    spis = spis.filter(Items.box_id == int(request.form['box_list']))
                if request.form["param_str"]:
                    test = True
                    spis = spis.filter(Items.param.like(f'%{request.form["param_str"]}%'))
                if request.form["comment_str"]:
                    test = True
                    spis = spis.filter(Items.comment.like(f'%{request.form["comment_str"]}%'))
                if test:
                    flash(u'Фильтр применён')
        if session.get('update_spis', False):
            session['update_spis'] = False
            if session.get('item_type_id', 0):
                spis = spis.filter(Items.item_type_id == session.get('item_type_id', 0))
            if session.get('place_id', 0):
                spis = spis.filter(Items.place_id == session.get('place_id', 0))
            if session.get('box_id', 0):
                spis = spis.filter(Items.box_id == session.get('box_id', 0))
        spis.all()
        view_form.class_list.data = session.get('class_type_id', 0)
        view_form.type_list.data = session.get('item_type_id', 0)
        view_form.place_list.data = session.get('place_id', 0)
        view_form.box_list.data = session.get('box_id', 0)
        return render_template("viewtable.html", form=view_form, items=spis)
    else:
        return redirect("/login")


@app.route('/viewitem/<int:item_id>', methods=['GET', 'POST'])
def viewitem(item_id):
    view_form = ViewTableForm()
    view_form.setup()
    db_sess = db_session.create_session()
    spis = db_sess.query(Items).filter(Items.id == item_id).first()
    if session.get('reset_viewform', False):
         view_form.class_list.data = session['class_type_id']
         view_form.type_list.data = session['item_type_id']
         view_form.place_list.data = session['place_id']
         view_form.box_list.data = session['box_id']

    if view_form.cancel_btn.data:
        session['update_spis'] = True
        return redirect('/viewtable')
    if view_form.validate_on_submit():
        session['update_spis'] = True
        if view_form.add_btn.data:
            if int(request.form['box_list']) and int(request.form['place_list']) and int(request.form['type_list']):
                obj = Items(int(request.form['type_list']), int(request.form['place_list']), int(request.form['box_list']),
                            request.form['param_str'], request.form['place_pos_str'], request.form['comment_str'])
                db_sess.add(obj)
                db_sess.commit()
                return redirect('/viewtable')
            else:
                session['class_type_id'] = view_form.class_list.data
                session['item_type_id'] = view_form.type_list.data
                session['place_id'] = view_form.place_list.data
                session['box_id'] = view_form.box_list.data
                session['reset_viewitem'] = True
                flash('Не установлены справочные значения')
        elif view_form.edit_btn.data:
            if int(request.form['box_list']) and int(request.form['place_list']) \
                and int(request.form['type_list']) and spis:
                spis.item_type_id = int(request.form['type_list'])
                spis.place_id = int(request.form['place_list'])
                spis.box_id = int(request.form['box_list'])
                spis.param = request.form['param_str']
                spis.place_pos = request.form['place_pos_str']
                spis.comment = request.form['comment_str']
                db_sess.merge(spis)
                db_sess.commit()
                return redirect('/viewtable')
            else:
                flash('Не установлены справочные значения')
        elif view_form.del_btn.data:
            db_sess.query(Items).filter(Items.id == item_id).delete()
            db_sess.commit()
            return redirect('/viewtable')
    if spis:
        view_form.class_list.data = spis.item_type.class_type_id
        view_form.type_list.data = spis.item_type_id
        view_form.place_list.data = spis.place_id
        view_form.box_list.data = spis.box_id
        view_form.param_str.data = spis.param
        view_form.place_pos_str.data = spis.place_pos
        view_form.comment_str.data = spis.comment
    else:
        view_form.class_list.data = session['class_type_id']
        view_form.type_list.data = session['item_type_id']
        view_form.place_list.data = session['place_id']
        view_form.box_list.data = session['box_id']
    return render_template("viewitem.html", form=view_form, items=spis, item_id=item_id)


@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.after_request
def after_request_callback( responce ):
    return responce

def main():
    db_session.global_init("db/database.db")
    app.register_blueprint(items_api.blueprint)
    app.run()


if __name__ == '__main__':
    main()