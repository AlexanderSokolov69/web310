from classes.cl_const import Const
from .cl__main_sqlobject import SQLObject


class Users(SQLObject):
    def set_sql(self, sql=None, ord=None):
        self.keys = (
            ('name', 'Фамилия И.О.:'),
            ('fam', 'Фамилия:'),
            ('ima', 'Имя:'),
            ('otch', 'Отчество:'),
            ('login', 'Логин для входа в программу:'),
            ('phone', 'Номер телефона:'),
            ('email', 'e-mail адрес:'),
            ('birthday', 'Дата рождения:'),
            ('idRoles', 'Роль доступа:'),
            ('idPlaces', 'Место работы/учёбы:'),
            ('comment', 'Дополнительная информация:'),
            ('sertificate', 'Сертификат ПФДО:'),
            ('navigator', 'Публикация в Навигаторе (1/0):')
        )
        self.dbname = 'users'
        if sql is None:
            self.sql = f"""select u.id, rtrim(u.name) as 'Фамилия И.О.', u.fam as 'Фамилия', u.ima as 'Имя', 
                u.otch as 'Отчество', u.login as 'Логин', u.phone as 'Телефон', 
                u.email as 'E-mail', u.birthday as 'Д.рожд', u.sertificate as 'Сертификат ПФДО',
                r.name as 'Роль', p.name as 'Место учёбы/работы', p.comment as 'Класс/Должн.',
                u.comment as 'Доп.информация', r.idPriv,  u.navigator
               from users u
               join roles r on u.idRoles = r.id
               join places p on u.idPlaces = p.id"""
        else:
            self.sql = f"""{sql}"""
        self.set_order(ord)

    def get_user_login(self, login):
        sql = f"select * from users where login = '{login.lower()}'"
        cur = self.con.cursor()
        data = cur.execute(sql).fetchone()
        if data:
            ret = {}
            for i, key in enumerate(cur.description):
                ret[key[0]] = data[i]
        else:
            ret = None
        return ret

    def set_user_password(self, id, passwd):
        sql = f"update users set passwd = ? where id = {id}"
        cur = self.con.cursor()
        cur.execute(sql, [passwd])
        self.con.commit()

    def priv_users(self, mask='1'):
        def check(priv, mask):
            for i, j in zip(mask, priv[:len(mask):1]):
                if i == '1' and i != j:
                    return False
            return True

        sql = f"""select distinct u.id, trim(u.name) as name, trim(u.comment), trim(p.access) from users u
                        join roles r on u.idRoles = r.id
        			    join priv p on r.idPriv = p.id
        			    order by name """
        spis = super().execute_command(sql)
        spis = [val[:3] for val in spis if check(val[3], mask)]
        return spis

if __name__ == '__main__':
    # us = Users(con)
    # print(us.get_user_login('falcon'))
    pass