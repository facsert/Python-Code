from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row
from psycopg import Cursor, Connection


class Database:
    
    connect: None | Connection = None
   
    @classmethod
    def connect_database(cls) -> None:
        if cls.connect is None or cls.connect.closed:
            cls.connect = psycopg.connect(
                host="localhost",
                port="5432",
                dbname="db",
                user="postgres",
                password="password"
            )
    
    @contextmanager
    @classmethod
    def create_session(cls):
        session = cls.connect.cursor(row_factory=dict_row)
        try:
            yield cls.session
        finally:
            session.close()
            cls.connect.commit()
        
    @classmethod
    def get_session(cls):
        return cls.connect.cursor(row_factory=dict_row)
        
    @classmethod
    def create_tables(cls):
        pass
    
    @classmethod
    def close(cls):
        cls.connect.close()
        
    @classmethod
    def init(cls):
        cls.connect_database()
        cls.create_tables()
