import datetime as dt
from sqlalchemy import Column, Integer, String, REAL, ForeignKey, DateTime
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    '''
    Пользователи доступа
    '''
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    fullname = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)
    created_date = Column(DateTime, default=dt.datetime.now)

    def __init__(self, name, fullname, hashed_password):
        self.name = name
        self.fullname = fullname
        self.hashed_password = hashed_password

    def __repr__(self):
        return f"<User('{self.name},{self.fullname}, {self.created_date})>"

    def check_password(self, test_pass):
        return (self.hashed_password == test_pass)

