import sqlite3
from classes.cl_const import Const


class Logger:
    def __init__(self, con):
        self.con = con
        self.cur = con.cursor()
        self.sql = "insert into log (uid, name, date, time, info) values (?, ?, ?, ?, ?)"

    def out(self, arg):
        self.keys = (
            ('uid', 'ID:'),
            ('name', 'FIO:'),
            ('date', 'Date:'),
            ('time', 'Time:'),
            ('info', 'Info:')
        )
        self.cur.execute(self.sql, arg)
        self.con.commit()

if __name__ == '__main__':
    con = sqlite3.connect('..\\db\\database_J.db')
    lg = Logger(con)
    [lg.out(('1', '2', '3', '4', '5')) for _ in range(10)]
    con.commit()
