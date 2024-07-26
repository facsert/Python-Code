from traceback import format_exc
from contextlib import contextmanager

import MySQLdb
from loguru import logger

CONFIG = {
    "host": "localhost",
    "port": "5432",
    "dbname": "learn",
    "user": "postgres",
    "password": "password",
}

class Database:
    """ mysql database """

    @contextmanager
    def __new__(cls, database=CONFIG):
        try:
            conn = MySQLdb.connect(database)
            yield conn.cursor(MySQLdb.cursors.DictCursor)
            conn.commit()
        except Exception as e:
            logger.error(f"{e}\n{format_exc}")
            _ = conn.rollback() if conn else None
        finally:
            _ = conn.close() if conn else None
