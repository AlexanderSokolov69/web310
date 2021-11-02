import datetime
import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .db_class_groups import Groups
from .db_class_places import Places
from .db_class_roles import Roles
from .db_class_users import Users
from .db_session import SqlAlchemyBase


class GroupTable(SqlAlchemyBase):
    __tablename__ = 'group_table'

    id = Column(Integer, primary_key=True, autoincrement=True)
    idGroups = Column(Integer, ForeignKey(Groups.id))
    idUsers = Column(Integer, ForeignKey(Users.id))
    comment = Column(String, nullable=True)
    groups = relationship(Groups)
    users = relationship(Users)
