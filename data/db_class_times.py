import datetime
import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
from flask import g

from .db_class_days import Days
from .db_class_groups import Groups
from .db_class_kabs import Kabs
from .db_class_places import Places
from .db_class_roles import Roles
from .db_session import SqlAlchemyBase


class Times(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'times'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
