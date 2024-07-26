from contextlib import contextmanager

import psycopg
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from loguru import logger


config = {
    "host": "localhost",
    "port": "5432",
    "dbname": "learn",
    "user": "postgres",
    "password": "password",
}

class Database:

    @classmethod
    def init(cls, db=None):
        """ connect database """

        db = db if db else config
        conn_str = " ".join([f"{k}={v}" for k, v in db.items()])
        cls.pool: ConnectionPool = ConnectionPool(min_size=1, max_size=10, conninfo=conn_str)
        return cls.pool

    @contextmanager
    def __new__(cls, db=None):
        _ = cls.init(db) if db is not None else None

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
            cls.pool.putconn(conn)

if __name__ == "__main__":
    Database.init()
    with Database() as cursor:
        cursor.execute("SELECT id, title FROM article")
        print(cursor.fetchall())

        

