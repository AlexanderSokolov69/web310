import datetime
import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
from flask import g

from .db_class_places import Places
from .db_class_roles import Roles
from .db_session import SqlAlchemyBase
from .misc import MyDict


class Monts(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'monts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    num = Column(Integer, nullable=True)
    name = Column(String, nullable=True)

    def get_dict(self):
        res = MyDict()
        spis = g.db_sess.query(Monts)
        for mn in spis:
            res[mn.num] = mn.name.strip()
        return res
