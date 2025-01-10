from typing import Literal
from traceback import format_exc
from contextlib import contextmanager
from dataclasses import dataclass, asdict

import MySQLdb
from loguru import logger

@dataclass
class DBConnect:
    """ 数据库连接 """
    host: str
    port: int
    db: str
    user: str
    password: str

server: DBConnect = DBConnect(
    host="localhost",
    port=3306,
    db="server",
    user="user",
    password="password"
)

backup: DBConnect = DBConnect(
    host="localhost",
    port=5432,
    db="backup",
    user="postgres",
    password="postgres"
)

DATABASE = [server, backup]
type DBName = Literal["server", "backup"]

class Database:
    """ mysql database """

    @classmethod
    def init(cls) -> None:
        """ 数据库初始化,连接测试 """
        _ = [MySQLdb.connect(**asdict(conn)).close() for conn in DATABASE]
        _ = [setattr(cls, conn.db, conn) for conn in DATABASE]

    @contextmanager
    def __new__(cls, dbname: DBName="server"):
        cursor, conn = None, None
        try:
            conn = MySQLdb.connect(**asdict(getattr(cls, dbname)))
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            yield cursor
            conn.commit()
        except Exception as e:
            logger.error(f"{e}\n{format_exc}")
            _ = conn.rollback() if conn else None
        finally:
            _ = cursor.close() if cursor else None
            _ = conn.close() if conn else None
