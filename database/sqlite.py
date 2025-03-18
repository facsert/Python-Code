import sqlite3
from typing import Literal
from contextlib import contextmanager
from dataclasses import dataclass, asdict

from loguru import logger


DATABASE: dict[str, str] = {
    "server": "server.db",
    "backup": "backup.db"
}
DBName = Literal[ "server", "backup"]

class Database:
    """ database module """
    
    @classmethod
    def dict_factory(cls, cursor, row):
        fields = [column[0] for column in cursor.description]
        return {key: value for key, value in zip(fields, row)}

    @contextmanager
    def __new__(cls, dbname: DBName="server"):
        conn = sqlite3.connect(DATABASE[dbname])
        conn.row_factory = cls.dict_factory
        try:
            cursor = conn.cursor()
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"database execute error: {e}")
        finally:
            conn and conn.close()

if __name__ == "__main__":
    with Database() as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS movies(title, year, score)")
        cur.execute("""
            INSERT INTO movies VALUES
                ('Monty Python and the Holy Grail', 1975, 8.2),
                ('And Now for Something Completely Different', 1971, 7.5)
        """)
    
    with Database() as cur:
        cur.execute("SELECT * FROM movies")
        print([dict(i) for i in cur.fetchall()])
