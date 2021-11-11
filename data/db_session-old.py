import urllib
import sqlalchemy as sa
import sqlalchemy.orm as orm
from flask import flash
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec
from data.cl_const import Const
from data.db_class_access import Access

SqlAlchemyBase = dec.declarative_base()
__factory = None


def global_init(db_file):
    global __factory
    if __factory:
        return
    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")
    conn_str = f"Driver=SQL Server;Server=172.16.1.12,1433;Database=Journal4303;UID=sa;PWD=Prestige2011!;"
    params = urllib.parse.quote_plus(conn_str)
    try:
        engine = sa.create_engine(f"mssql+pyodbc:///?odbc_connect={params}", echo=Const.TEST_MODE)
        #    engine = sa.create_engine("mssql+pyodbc://sa:Prestige2011!@172.16.1.12:1433/Journal4303", echo=Const.TEST_MODE)
        __factory = orm.sessionmaker(bind=engine)
        SqlAlchemyBase.metadata.create_all(engine)
    except Exception as err:
        flash(f"Ошибка подключения SQL: {err}", category='error')
        __factory = None


def create_session() -> Session:
    global __factory
    # return None
    try:
        return __factory()
    except Exception as err:
        flash(f"Ошибка создания сессии: {err}", category='error')


def access_action(*args, **kwargs):
    # with create_session() as db_sess:
    user = Access(**kwargs)
    g.db_sess.add(user)
    g.db_sess.commit()


def executeSQL(func):
    try:
        ret = eval(func)
        return ret
    except Exception as err:
        flash(f"Ошибка обработки SQL", category='error')
        return None
