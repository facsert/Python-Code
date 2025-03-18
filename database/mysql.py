from typing import Literal
from traceback import format_exc
from contextlib import contextmanager
from dataclasses import dataclass, asdict

# import MySQLdb
from dbutils.pooled_db import PooledDB
import pymysql
from pymysql import Error
from pymysql.cursors import DictCursor
from loguru import logger

# pip install pymysql dbutils 


@dataclass
class DBConnect:
    """ 数据库连接 """
    host: str
    port: int
    database: str
    user: str
    password: str

server: DBConnect = DBConnect(
    host="localhost",
    port=3306,
    database="server",
    user="user",
    password="password"
)

backup: DBConnect = DBConnect(
    host="localhost",
    port=3306,
    database="backup",
    user="user",
    password="password"
)

DATABASE: list[DBConnect] = [server, backup]
DBName = Literal["server", "backup"]

class Database:
    """ mysql database """

    @classmethod
    def init(cls) -> None:
        """ 数据库初始化,连接测试 """
        for conn in DATABASE:
            if getattr(cls, conn.database, None) is not None:
                continue
            
            setattr(cls, conn.database, PooledDB(
                **asdict(conn),
                creator=pymysql,
                maxconnections=10,
                mincached=1,
                cursorclass=DictCursor,
                autocommit=True,
            ))

    @contextmanager
    def __new__(cls, dbname: DBName="backup"):
        cls.init()
        pool = getattr(cls, dbname, None)
        try:
            with pool.connection() as conn:
                with conn.cursor() as cursor:
                    yield cursor
        except Exception as e:
            logger.error(f"database execute error: {e}")

if __name__ == '__main__':
    Database.init()
    with Database() as cur:
        cur.execute("SELECT * FROM nodes LIMIT 3")
        print(cur.fetchall())