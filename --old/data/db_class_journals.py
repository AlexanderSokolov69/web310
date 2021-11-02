import datetime
import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .db_class_courses import Courses
from .db_class_groups import Groups
from .db_class_places import Places
from .db_class_roles import Roles
from .db_class_users import Users
from .db_session import SqlAlchemyBase


class Journals(SqlAlchemyBase):
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
    comment = Column(String, nullable=True)
    usecomm = Column(String, nullable=True)
    groups = relationship(Groups)
