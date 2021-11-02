import datetime
import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .db_class_places import Places
from .db_class_roles import Roles
from .db_session import SqlAlchemyBase


class Monts(SqlAlchemyBase):
    __tablename__ = 'monts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    num = Column(Integer, nullable=True)
    name = Column(String, nullable=True)
