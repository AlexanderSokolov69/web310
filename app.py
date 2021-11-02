from flask import Flask, render_template
from flask_login import LoginManager

from models.m_users import UsersModel
from tools import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.user_repo = UsersModel()


@app.route("/")
def root():
    return app.send_static_file("index.html")


@app.route("/api/register", methods=['POST'])
def user_register():
    pass


if __name__ == '__main__':
    db_session.global_init("DSN=it-cube64")
    app.run()
