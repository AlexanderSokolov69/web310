import sys
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PyQt5.QtWidgets import QApplication, QTableView

app = QApplication(sys.argv)
db = QSqlDatabase.addDatabase('QODBC')
conn_str = f"""Driver=SQL Server;Server=172.16.1.12,1433;Database=Journal4303;uid=sa;pwd=Prestige2011!"""
# conn_str = f"""DSN=it-cube64;uid=sa;pwd=Prestige2011!"""
db.setDatabaseName(conn_str)

if db.open():
    pass
else:
    print(db.lastError().text())
    sys.exit()
# spis = db.tables()
# for n in spis:
#     print(f"{n:16}", end='')
#     sp = []
#     for i in range(db.record(n).count()):
#         sp.append(db.record(n).fieldName(i))
#     print('[', ', '.join(sp), ']')
#
query = QSqlQuery()
query.prepare('select * from users')
query.exec()
model = QSqlTableModel()
model.setTable('users')
model.select()
table = QTableView()
table.setModel(model)

table.show()

sys.exit(app.exec())

# query.next()
# while query.isValid():
#     print(query.value('name'))
#     query.next()
