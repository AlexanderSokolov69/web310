import pyodbc
from flask import Flask

from data import db_session
from data.db_class_users import Users

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session.global_init("DSN=it-cube64")
    db_sess = db_session.create_session()
    user = db_sess.query(Users).where(Users.id == 19).first()
    print(user.name)

#    app.run()


if __name__ == '__main__':
    main()

