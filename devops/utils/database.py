import atexit
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from os import getenv
from typing import Literal

from loguru import logger
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool


DBName = Literal["base"]

@dataclass
class DBConnect:
    """ 数据库连接 """
    host: str
    port: int
    dbname: DBName
    user: str
    password: str

base: DBConnect = DBConnect(
    host="192.168.0.30",
    port=5432,
    dbname="base",
    user=getenv("DB_USERNAME", "root"),
    password=getenv("DB_PASSWORD", "admin"),
)

# backup: DBConnect = DBConnect(
#     host="localhost",
#     port=5432,
#     dbname="backup",
#     user="postgres",
#     password="postgres"
# )

DATABASE: list[DBConnect] = [base]


class Database:
    """ database module """
    is_init: bool = False
    pools: dict[DBName, ConnectionPool] = {}
    
    @classmethod
    def init(cls) -> None:
        """ 数据库初始化连接 """
        if cls.is_init:
            return

        for conn in DATABASE:
            if conn.dbname in cls.pools:
                continue

            cls.pools[conn.dbname] = ConnectionPool(
                min_size=1,
                max_size=5,
                conninfo=" ".join(f"{k}={v}" for k, v in asdict(conn).items())
            )

        cls.is_init = True
        atexit.register(cls.close)

    @contextmanager
    def __new__(cls, dbname: DBName="base"):
        cls.init()
        pool: ConnectionPool|None = cls.pools.get(dbname, None)

        conn = None
        if pool is None:
            raise KeyError(f"connect pool {dbname} not exist")

        try:
            with pool.connection() as conn:
                with conn.cursor(row_factory=dict_row) as cursor:
                    yield cursor
        except Exception as err:
            logger.error(f"database execute error: {err}")

    @classmethod
    def close(cls):
        for name, pool in list(cls.pools.items()):
            if not pool.closed:
                pool.close()
            del cls.pools[name]
        cls.is_init = False


if __name__ == "__main__":
    # Database.init()
    with Database() as cursor:
        cursor.execute('SELECT * FROM "users"')
        print(cursor.fetchall())


