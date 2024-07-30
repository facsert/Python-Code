from contextlib import contextmanager
from dataclasses import dataclass

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

DEFAULT_DATABASE: DBConnect = DBConnect(
    host="localhost",
    port="5432",
    dbname="postgres",
    user="postgres",
    password="password"
)

class Database:
    """ database module """
    pool: ConnectionPool| None = None
    db: DBConnect = DEFAULT_DATABASE

    @classmethod
    def init(cls, db: DBConnect|None=None) -> None:
        """ 数据库初始化连接 """
        cls.db = db if db else cls.db
        cls.pool = ConnectionPool(
            min_size=1,
            max_size=10,
            conninfo=" ".join(f"{k}={v}" for k, v in vars(cls.db).items())
        )

    @contextmanager
    def __new__(cls, db: DBConnect|None=None):
        _ = cls.init(db) if db else None
        try:
            conn = cls.pool.getconn()
            cursor = conn.cursor(row_factory=dict_row)
            yield cursor
            conn.commit()
        except Exception as e:
            _ = conn.rollback() if conn else None
            logger.error(f"error: {e}")
        finally:
            _ = cursor.close() if cursor else None
            _ = cls.pool.putconn(conn) if cls.pool else None

if __name__ == "__main__":
    Database.init()
    with Database() as cur:
        cur.execute("SELECT id, title FROM article")
        print(cur.fetchall())
