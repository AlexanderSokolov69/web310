from sqlalchemy import Column, Integer, String, REAL, ForeignKey, DateTime, orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Items(SqlAlchemyBase, SerializerMixin):
    '''
    Объекты хранения
    '''
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    item_type_id = Column(
        Integer,
        ForeignKey('item_type.id'),
        nullable=False,
    )
    place_id = Column(
        Integer,
        ForeignKey('place.id'),
        nullable=False,
    )
    box_id = Column(
        Integer,
        ForeignKey('box.id'),
        nullable=False,
    )
    param = Column(String)
    place_pos = Column(String)
    comment = Column(String)
    item_type = orm.relation('Item_type')
    place = orm.relation('Place')
    box = orm.relation('Box')

    def __init__(self, item_type_id, place_id, box_id, param, place_pos, comment):
        self.item_type_id = item_type_id
        self.place_id = place_id
        self.box_id = box_id
        self.param = param
        self.place_pos = place_pos
        self.comment = comment

    def __repr__(self):
        return f"<Items({self.item_type.name}, {self.param}{self.item_type.param}, " \
               f"{self.box.name} [{self.place_pos}], {self.place.name})>"
