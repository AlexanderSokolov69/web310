from sqlalchemy import Column, Integer, String, REAL, ForeignKey, DateTime, orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Place(SqlAlchemyBase, SerializerMixin):
    '''
    Место хранения
    '''
    __tablename__ = 'place'
    STATUS_INITIAL = 1
    id = Column(Integer, primary_key=True)
    name = Column(String)
    param = Column(String)
    items = orm.relation("Items", back_populates='place')

    def __init__(self, name, param):
        self.name = name
        self.param = param

    def __repr__(self):
        return f"<Place({self.name},{self.param})>"
