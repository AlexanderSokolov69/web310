import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Roles(SqlAlchemyBase):
    __tablename__ = 'roles'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
# idPriv
    comment = sqlalchemy.Column(sqlalchemy.String, nullable=True)
