import datetime
import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin

from .db_class_places import Places
from .db_class_roles import Roles
from .db_session import SqlAlchemyBase


class Kabs(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'kabs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    color = Column(String, nullable=True)
