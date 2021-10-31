from sqlalchemy import Column, Integer, String, REAL, ForeignKey, DateTime, orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Item_type(SqlAlchemyBase, SerializerMixin):
    '''
    Тип объекта хранения
    '''
    __tablename__ = 'item_type'
    STATUS_INITIAL = 1
    id = Column(Integer, primary_key=True)
    class_type_id = Column(
        Integer,
        ForeignKey('class_type.id'),
        nullable = False,
    )
    name = Column(String)
    param = Column(String)
    mult = Column(REAL)
    class_type = orm.relation('Class_type')
    items = orm.relation("Items", back_populates='item_type')

    def __init__(self, clas_type_id, name, param, mult):
        self.class_type_id = clas_type_id
        self.name = name
        self.param = param
        self.mult = mult

    def __repr__(self):
        return f"<Item_type({self.name},{self.param}, {self.mult})>"
