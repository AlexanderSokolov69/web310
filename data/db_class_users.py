import datetime
import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .db_class_places import Places
from .db_class_roles import Roles
from .db_session import SqlAlchemyBase


class Users(SqlAlchemyBase):
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
