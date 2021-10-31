from sqlalchemy import Column, Integer, String, REAL, ForeignKey, DateTime, orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Class_type(SqlAlchemyBase, SerializerMixin):
    '''
    Класс объекта хранения
    '''
    __tablename__ = 'class_type'
    STATUS_INITIAL = 1
    id = Column(Integer, primary_key=True)
    name = Column(String)
    param = Column(String)
    item_type = orm.relation("Item_type", back_populates='class_type')

    def __init__(self, name, param):
        self.name = name
        self.param = param

    def __repr__(self):
        return f"<Class_type({self.name},{self.param})>"

