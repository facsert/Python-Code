from typing import Literal
from contextlib import contextmanager
from dataclasses import dataclass, asdict

from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from loguru import logger


@dataclass
class DBConnect:
    """ 数据库连接 """
    host: str
    port: int
    dbname: str
    user: str
    password: str

server: DBConnect = DBConnect(
    host="localhost",
    port=5432,
    dbname="server",
    user="postgres",
    password="postgres"
)

backup: DBConnect = DBConnect(
    host="localhost",
    port=5432,
    dbname="backup",
    user="postgres",
    password="postgres"
)

DATABASE: list[DBConnect] = [server, backup]
DBName = Literal[ "server", "backup"]

class Database:
    """ database module """
    is_init: bool = False
    pools: dict[str, ConnectionPool] = {}
    
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
    def __new__(cls, dbname: DBName="server"):
        cls.init()
        pool: ConnectionPool = cls.pools.get(dbname, None)

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
            pool.closed is False and pool.close()
            del cls.pools[name]
        cls.is_init = False

if __name__ == "__main__":
    Database.init()
    with Database() as cursor:
        nodes = cursor.execute("SELECT * FROM nodes LIMIT 3").fetchall()
        print(nodes)

    with Database("backup") as cursor:
        nodes = cursor.execute("SELECT * FROM nodes LIMIT 3").fetchall()
        print(nodes)

