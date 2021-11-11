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


class Rasp(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'rasp'

    id = Column(Integer, primary_key=True, autoincrement=True)
    idGroups = Column(Integer, ForeignKey(Groups.id))
    idKabs = Column(Integer, ForeignKey(Kabs.id))
    idDays = Column(Integer, ForeignKey(Days.id))
    tstart = Column(String, nullable=True)
    tend = Column(String, nullable=True)
    comment = Column(String, nullable=True)
    name = Column(String, nullable=True)
    groups = relationship(Groups)
    kabs = relationship(Kabs)
    days = relationship(Days)

    def __repr__(self):
        return f"<Rasp(id:{self.id},idGroups:{self.idGroups}, name:{self.name})>"
