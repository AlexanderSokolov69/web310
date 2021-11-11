import datetime
import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
from flask import g

from .cl_const import Const
from .db_class_courses import Courses
from .db_class_groups import Groups
from .db_class_places import Places
from .db_class_roles import Roles
from .db_class_users import Users
from .db_session import SqlAlchemyBase


class Journals(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'journals'
    id = Column(Integer, primary_key=True, autoincrement=True)
    idGroups = Column(Integer, ForeignKey(Groups.id))
    date = Column(String, nullable=True)
    tstart = Column(String, nullable=True)
    tend = Column(String, nullable=True)
    name = Column(String, nullable=True)
    present = Column(String, nullable=True)
    estim = Column(String, nullable=True)
    shtraf = Column(String, nullable=True)
    usercomm = Column(String, nullable=True)
    comment = Column(String, nullable=True)
    groups = relationship(Groups)

    def __init__(self, *args, **kwargs):
        super(Journals, self).__init__()
        try:
            self.idGroups = kwargs['idGroups']
            self.date = kwargs['date']
            self.tstart = kwargs.get('tstart', '08:00')
            self.tend = kwargs.get('tend', '09:30')
            self.name = kwargs.get('name', 'Новая тема')
            self.present = kwargs.get('present', '')
            self.estim = kwargs.get('estim', '')
            self.shtraf = kwargs.get('shtraf', '')
            self.usercomm = kwargs.get('usercomm', '')
            self.comment = kwargs.get('comment', '')
        except KeyError as err:
            if Const.TEST_MODE:
                print(err)
                raise KeyError