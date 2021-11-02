import datetime
import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from tools.db_session import SqlAlchemyBase


class Priv(SqlAlchemyBase):
    __tablename__ = 'priv'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    access = Column(String, nullable=True)
    comment = Column(String, nullable=True)
