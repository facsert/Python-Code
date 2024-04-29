
import psycopg
from psycopg.rows import dict_row
from psycopg import Cursor, Connection
from pymongo import MongoClient, ASCENDING

MongoDB = MongoClient("mongodb://localhost:27017")

nodedb = MongoDB['nodedb']                       # 创建数据库(不存在则创建)
Nodes = nodedb['nodes']                          # 创建集合(不存在则创建)

Nodes.create_index(                              # 设置 host 和 port 复合唯一约束
    [('host', ASCENDING), ('port', ASCENDING)],
    unique=True
)


class Database:
    
    connect: None | Connection = None
    session: None | Cursor = None
    
    @classmethod
    def connect_database(cls) -> None:
        cls.connect = psycopg.connect(
            host="localhost",
            port="5432",
            dbname="db",
            user="postgres",
            password="password"
        )
    
    @classmethod
    def create_session(cls):
        cls.session = cls.connect.cursor(row_factory=dict_row)
        yield cls.session
        
        cls.session.close()
        cls.connect.commit()
        
    @classmethod
    def create_tables(cls):
        session = cls.connect.cursor()
        session.execute("""
            CREATE TABLE IF NOT EXISTS person (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                age INTEGER NOT NULL,
                locked BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            );
        """)
        session.close()
        
    @classmethod
    def close(cls):
        cls.connect.close()
        
    @classmethod
    def init(cls):
        cls.connect_database()
        cls.create_tables()
