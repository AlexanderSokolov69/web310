from requests import get, post, delete

print(delete('http://localhost:5000/api/items/999').json())
print(delete('http://localhost:5000/api/items/10').json())
# print(post('http://localhost:5000/api/items', json={
#     'item_type_id': '1',
#     'place_id': '1',
#     'box_id': '1',
#     'param': 'Параметр',
#     'place_pos': 'Место',
#     'comment': 'Коммент'
# }).json())

# item_type_id, place_id, box_id, param, place_pos, comment