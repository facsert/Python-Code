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
    port="5432",
    dbname="server",
    user="postgres",
    password="postgres"
)

backup: DBConnect = DBConnect(
    host="localhost",
    port="5432",
    dbname="backup",
    user="postgres",
    password="postgres"
)

DATABASE = [server, backup]
type DBName = Literal[ "server", "backup"]

class Database:
    """ database module """

    @classmethod
    def init(cls) -> None:
        """ 数据库初始化连接 """
        connect = lambda conn: ConnectionPool(
            min_size=1,
            max_size=10,
            conninfo=" ".join(f"{k}={v}" for k, v in asdict(conn).items())
        )
        _ = [setattr(cls, conn.dbname, connect(conn)) for conn in DATABASE]

    @contextmanager
    def __new__(cls, dbname: DBName="server"):
        pool = getattr(cls, dbname)
        _ = cls.init() if pool is None else None
        cursor, conn = None, None
        try:
            conn = pool.getconn()
            cursor = conn.cursor(row_factory=dict_row)
            yield cursor
            conn.commit()
        except Exception as e:
            _ = conn.rollback() if conn else None
            logger.error(f"error: {e}")
        finally:
            _ = cursor.close() if cursor else None
            _ = pool.putconn(conn) if pool else None

if __name__ == "__main__":
    Database.init()
    with Database() as cursor:
        nodes = cursor.execute("SELECT * FROM nodes LIMIT 3").fetchall()
        print(nodes)

    with Database("backup") as cursor:
        nodes = cursor.execute("SELECT * FROM nodes LIMIT 3").fetchall()
        print(nodes)

