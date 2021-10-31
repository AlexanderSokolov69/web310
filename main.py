import pyodbc
from flask import Flask

from data import db_session
from data.cl_const import Const
from data.db_class_priv import Priv
from data.db_class_roles import Roles
from data.db_class_users import Users

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session.global_init("DSN=it-cube64")
    db_sess = db_session.create_session()
    user = db_sess.query(Users).join(Roles).join(Priv)
    for us in user.where(Priv.access.like(Const.ACC_CUBIST)):
        print(us.name, us.roles.priv.access)
    cub = user.where(Priv.access.like(Const.ACC_CUBIST))
    print(cub.count())

#    app.run()


if __name__ == '__main__':
    main()

