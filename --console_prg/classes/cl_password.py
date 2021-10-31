import os
import hashlib
from classes.cl_const import Const


class Password:
    """ Работа с паролями. упаковка/распаковка """
    def __init__(self, passwd=''):
        self.N = 8
        salt = os.urandom(self.N)
        psw = self.make_key(passwd, salt)
        self.storage = salt + psw

    def make_key(self, passwd, salt):
        return hashlib.pbkdf2_hmac(
            'sha256',  # Используемый алгоритм хеширования
            passwd.encode('utf-8'),  # Конвертируется пароль в байты
            salt,  # Предоставляется соль
            10000)

    def get_storage(self):
        return self.storage

    def set_storage(self, storage):
        self.storage = storage

    def check_passwd(self, passwd):
        salt = self.storage[:self.N]
        psw = self.storage[self.N:]
        chk = self.make_key(passwd, salt)
        psw = psw[:len(chk): 1]
        return psw == chk


if __name__ == '__main__':
    ph = Password(input())
    print(ph.get_storage())
