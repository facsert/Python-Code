'''
Author: facsert
Date: 2023-12-07 22:52:01
LastEditTime: 2023-12-07 23:45:20
LastEditors: facsert
Description: 
'''

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

path = "/root/Desktop/Python/database/db.db"
engine = create_engine(f"sqlite:///{path}", echo=True)

Base = declarative_base()
Base.metadata.create_all(engine, checkfirst=True)

class DB:
    
    def __new__(cls) -> None:
        cls.session = sessionmaker(bind=engine)()

    @classmethod    
    def add(cls, line: Base):
        cls.session.add(line)
        cls.session.commit()

    @classmethod    
    def select(cls, table: Base, expression: str, first: bool=False):
        table = cls.session.query(table)
        array = table.filter(eval(expression)) if expression else table        
        return array.first() if first else array

    @classmethod    
    def update(cls, table: Base, expression:str, target:dict, first: bool=False): 
        if first:
            line, key, value = cls.select(table, expression, True), target.popitem()
            setattr(line, key, value)
        else:
            cls.session.query(table).filter(eval(expression)).update(target)
        cls.session.commit()

    @classmethod    
    def delete(cls, table: Base, expression:str, first: bool=False):
        if first:
            cls.session.delete(cls.select(table, expression, True))
        else:
            cls.session.query(table).filter(eval(expression)).delete()
        cls.session.commit()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    
    def __repr__(self):
        return f"<User(name={self.name}, age={self.age})>"
    

if __name__ == "__main__":
    DB()
    DB.add(User(name="petter", age=23))
    DB.add(User(name="lily", age=18))
    DB.update(User, "User.name == 'petter'", {'age': 19}, first=True)
    DB.delete(User, "User.age == 18", first=True)
    users = DB.select(User, "")
    [print(user) for user in users]