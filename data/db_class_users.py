import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
from .cl_password import Password
from .db_class_places import Places
from .db_class_roles import Roles
from .db_session import SqlAlchemyBase
from flask import g


class Users(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fam = Column(String, nullable=True)
    ima = Column(String, nullable=True)
    otch = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    birthday = Column(String, nullable=True)
    comment = Column(String, nullable=True)
    name = Column(String, nullable=True)
    passwd = Column(String, nullable=True)
    login = Column(String, nullable=True)
    sertificate = Column(String, nullable=True)
    navigator = Column(String, nullable=True)
    winlogin = Column(String, nullable=True)
    idRoles = Column(Integer, ForeignKey(Roles.id))
    idPlaces = Column(Integer, ForeignKey(Places.id))
    places = relationship(Places)
    roles = relationship(Roles)

    def __repr__(self):
        return f"<Users(id:{self.id},name:{self.name}, winlogin:{self.winlogin})>"

    def check_password(self, passw):
        psw = Password()
        psw.set_storage(self.passwd)
        return psw.check_passwd(passw)

    def set_password(self, passw, login):
        psw = Password(passw)
        self.login = login
        self.passwd = psw.get_storage()
