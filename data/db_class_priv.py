import datetime
import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase


class Priv(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'priv'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    access = Column(String, nullable=True)
    comment = Column(String, nullable=True)
