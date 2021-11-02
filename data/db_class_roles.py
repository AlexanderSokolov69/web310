import datetime
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin

from .db_class_priv import Priv
from .db_session import SqlAlchemyBase


class Roles(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    idPriv = Column(Integer, ForeignKey(Priv.id))
    comment = Column(String, nullable=True)
    priv = relationship(Priv)
