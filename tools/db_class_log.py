import datetime
import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .db_class_places import Places
from .db_class_roles import Roles
from .db_session import SqlAlchemyBase


class Log(SqlAlchemyBase):
    __tablename__ = 'log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    date = Column(String, nullable=True)
    time = Column(String, nullable=True)
    info = Column(String, nullable=True)
    uid = Column(String, nullable=True)
