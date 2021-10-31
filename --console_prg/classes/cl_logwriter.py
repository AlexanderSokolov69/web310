from PyQt5.QtCore import QObject
from classes.cl_const import Const
import datetime


class LogWriter(QObject):
    def __init__(self, fname='errorlog.txt'):
        super(LogWriter, self).__init__()
        self.fname = fname

    def to_log(self, message):
        timestamp = datetime.datetime.now()
        with open(self.fname, 'a', encoding='utf8') as f:
            f.write(f"""{timestamp} ==> {message}\n<===\n""")

