import datetime
import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
from flask import g

from .db_class_places import Places
from .db_class_roles import Roles
from .db_class_users import Users
from .db_session import SqlAlchemyBase


class Courses(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    volume = Column(Integer, nullable=True)
    lesson = Column(Integer, nullable=True)
    url = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    target = Column(String, nullable=True)
    comment = Column(String, nullable=True)
    acchour = Column(Integer, nullable=True)
    hday = Column(Integer, nullable=True)
