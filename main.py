import pyodbc
from flask import Flask, render_template

from data import db_session
from data.cl_const import Const
from data.db_class_courses import Courses
from data.db_class_days import Days
from data.db_class_groups import Groups
from data.db_class_kabs import Kabs
from data.db_class_priv import Priv
from data.db_class_rasp import Rasp
from data.db_class_roles import Roles
from data.db_class_users import Users

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

@app.route("/")
def index():
    db_sess = db_session.create_session()
    rsp = db_sess.query(Rasp).order_by(Rasp.idDays, Rasp.tstart, Rasp.idKabs).all()
    # for us in rsp:
    #     print(us.days.name.strip(), us.tstart, us.tend, us.kabs.name,
    #           f"{us.groups.name.strip()} {us.groups.comment.strip()}",
    #           us.groups.users.name.strip(), us.groups.courses.name.strip(),
    #           us.comment)

    return render_template("rasp_view.html", items=rsp)

def main():
    db_session.global_init("DSN=it-cube64")
    app.run()


if __name__ == '__main__':
    main()

