import datetime
import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from .db_class_places import Places
from .db_class_roles import Roles
from .db_class_users import Users
from .db_session import SqlAlchemyBase


class Access(SqlAlchemyBase):
    __tablename__ = 'access'

    id = Column(Integer, primary_key=True, autoincrement=True)
    idUser = Column(Integer, ForeignKey(Users.id))
    idRole = Column(Integer, ForeignKey(Roles.id))
    datetime = Column(DateTime, default=datetime.datetime.now)
    sel = Column(String, nullable=True)
    users = relationship(Users)
    roles = relationship(Roles)
