import datetime
import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
from flask import g

from .db_class_courses import Courses
from .db_class_places import Places
from .db_class_roles import Roles
from .db_class_users import Users
from .db_session import SqlAlchemyBase


class Groups(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    idUsers = Column(Integer, ForeignKey(Users.id))
    idCourses = Column(Integer, ForeignKey(Courses.id))
    comment = Column(String, nullable=True)
    users = relationship(Users)
    courses = relationship(Courses)
