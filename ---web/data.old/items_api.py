import flask
from flask import jsonify, request
from . import db_session
from .items import Items


blueprint = flask.Blueprint('items_api', __name__, template_folder='templates')


@blueprint.route('/api/items')
def get_items():
    db_sess = db_session.create_session()
    result = db_sess.query(Items).all()
    return jsonify({
        'items': [item.to_dict(only=('id',
                                     'item_type.name',
                                     'param', 'item_type.param',
                                     'box.name', 'place_pos', 'comment'
                                     )) for item in result]
    })


@blueprint.route('/api/items/<int:item_id>', methods=['GET'])
def get_one_item(item_id):
    db_sess = db_session.create_session()
    result = db_sess.query(Items).get(item_id)
    if not result:
        return jsonify(({'error': 'Not found, wrong id'}))
    return jsonify({
        'items': result.to_dict(only=('id', 'param', 'place_pos', 'comment'))
    })


@blueprint.route('/api/items', methods=['POST'])
def create_item():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['item_type_id', 'place_id', 'box_id', 'param', 'place_pos', 'comment']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    crea = Items(
        item_type_id=request.json['item_type_id'],
        place_id=request.json['place_id'],
        box_id=request.json['box_id'],
        param=request.json['param'],
        place_pos=request.json['place_pos'],
        comment=request.json['comment']
    )
    db_sess.add(crea)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    db_sess = db_session.create_session()
    result = db_sess.query(Items).get(item_id)
    if not result:
        return jsonify(({'error': 'Not found'}))
    db_sess.query(Items).filter(Items.id == item_id).delete()
    db_sess.commit()
    return jsonify({'success': 'OK'})
