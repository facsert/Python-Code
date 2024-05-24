
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
        session = cls.connect.cursor(row_factory=dict_row)
        yield cls.session
        
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
