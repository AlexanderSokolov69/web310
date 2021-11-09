import datetime
import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin

from . import db_session
from .db_class_places import Places
from .db_class_roles import Roles
from .db_class_users import Users
from .db_session import SqlAlchemyBase


class Access(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'access'

    id = Column(Integer, primary_key=True, autoincrement=True)
    idUser = Column(Integer, ForeignKey(Users.id))
    idRole = Column(Integer, ForeignKey(Roles.id))
    datetime = Column(DateTime, default=datetime.datetime.now)
    sel = Column(String, nullable=True)
    users = relationship(Users)
    roles = relationship(Roles)

    def __init__(self, *args, **kwargs):
        super(Access, self).__init__(*args, **kwargs)
        self.idUser = kwargs.get('idUser', None)
        self.idRole = kwargs.get('idRole', None)
        self.datetime = datetime.datetime.now()
        self.sel = kwargs.get('sel', '')


def access_action(**kwargs):
    with db_session.create_session() as db_sess:
        user = Access(**kwargs)
        db_sess.add(user)
        db_sess.commit()


