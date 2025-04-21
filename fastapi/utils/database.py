import atexit
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
    
    inited: bool = False
    
    @classmethod
    def init(cls) -> None:
        """ 数据库初始化连接 """
        
        if cls.inited:
            return

        for conn in DATABASE:
            if getattr(cls, conn.dbname, None) is not None:
                continue

            setattr(cls, conn.dbname, ConnectionPool(
                min_size=1,
                max_size=10,
                conninfo=" ".join(f"{k}={v}" for k, v in asdict(conn).items())
            ))
        
        atexit.register(cls.close)
        cls.inited = True

    @contextmanager
    def __new__(cls, dbname: DBName="base"):
        cls.init()
        pool: ConnectionPool = getattr(cls, dbname, None)
        try:
            with pool.connection() as conn:
                with conn.cursor(row_factory=dict_row) as cursor:
                    yield cursor
        except Exception as err:
            logger.error(f"db execute error: {err}")
    
    @classmethod
    def close(cls) -> None:
        """ 数据库连接关闭 """
        for conn in DATABASE:
            pool: ConnectionPool = getattr(cls, conn.dbname, None)
            pool and pool.close()


if __name__ == "__main__":
    Database.init()
    with Database() as cursor:
        nodes = cursor.execute("SELECT * FROM nodes LIMIT 3").fetchall()
        print(nodes)

    with Database("backup") as cursor:
        nodes = cursor.execute("SELECT * FROM nodes LIMIT 3").fetchall()
        print(nodes)

