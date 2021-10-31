import urllib
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec
from data.cl_const import Const


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
    engine = sa.create_engine(f"mssql+pyodbc:///?odbc_connect={params}", echo=Const.TEST_MODE)
#    engine = sa.create_engine("mssql+pyodbc://sa:Prestige2011!@172.16.1.12:1433/Journal4303", echo=Const.TEST_MODE)

    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
