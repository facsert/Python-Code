'''
Author: facsert
Date: 2023-12-07 22:52:01
LastEditTime: 2023-12-10 20:57:19
LastEditors: facsert
Description: 
'''

from sqlalchemy import create_engine, select, update, delete, insert, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

path = "/root/Desktop/Python/fastapi/database/fastapi.db"
engine = create_engine(f"sqlite:///{path}", 
    echo=True,future=True,
)

Base = declarative_base()
Base.metadata.create_all(engine, checkfirst=True)

class DB:
    def __new__(cls) -> None:
        cls.session = Session(engine)

    @classmethod    
    def insert(cls, table: Base, *lines:dict):
        """ 新增数据 """
        array = cls.session.execute(insert(table).returning(table), lines)
        cls.session.commit()
        return array.all()

    @classmethod    
    def select(cls, table: Base, expr: str, first:bool=False):
        """ 筛选数据 """
        stmt = select(table).where(eval(expr) if expr else True)
        return cls.session.scalar(stmt) if first else cls.session.scalars(stmt)

    @classmethod   
    def update(cls, table: Base, expr: str, *lines:dict):
        """ 更新数据 """
        stmt, lines = (update(table).where(eval(expr)), lines) if expr else (update(table), list(lines))
        cls.session.execute(stmt, lines)
        cls.session.commit()

    @classmethod    
    def delete(cls, table: Base, expr: str):
        """ 删除数据 """
        array = cls.session.execute(delete(table).where(eval(expr)).returning(table))
        cls.session.commit()
        return array.all()
    
# class DB:
    
#     def __new__(cls) -> None:
#         cls.session = sessionmaker(bind=engine)()

#     @classmethod    
#     def add(cls, *lines: Base):
#         cls.session.add_all(list(lines))
#         cls.session.commit()

#     @classmethod    
#     def select(cls, table: Base, expression: str, first: bool=False):
#         table = cls.session.query(table)
#         array = table.filter(eval(expression)) if expression else table        
#         return array.first() if first else array

#     @classmethod    
#     def update(cls, table: Base, expression:str, target:dict, first: bool=False): 
#         if first:
#             line, key, value = cls.select(table, expression, True), target.popitem()
#             setattr(line, key, value)
#         else:
#             cls.session.query(table).filter(eval(expression)).update(target)
#         cls.session.commit()

#     @classmethod    
#     def delete(cls, table: Base, expression:str, first: bool=False):
#         if first:
#             cls.session.delete(cls.select(table, expression, True))
#         else:
#             cls.session.query(table).filter(eval(expression)).delete()
#         cls.session.commit()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    
    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, age={self.age})>"
    

if __name__ == "__main__":
    DB()
    [print(user) for user in DB.select(User, "")]