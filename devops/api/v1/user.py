from datetime import datetime

from loguru import logger
from fastapi import APIRouter, Depends

from service.auth import Auth
from utils.database import Database
from utils.schemas import Response, UserUpdate, UserCreate

router = APIRouter()
TABLE = "users"

@router.get('/users')
def get_users(name: str = Depends(Auth.curr_user)):
    """ 获取所有用户 """
    sql: str = f"SELECT * FROM {TABLE} WHERE deleted_at IS NULL"
    with Database() as cursor:
        cursor.execute(sql)
        users = cursor.fetchall()
    logger.info(f"user {name} get users")
    return Response(users)

@router.get('/users/{id}')
def get_user(id: int, name: str = Depends(Auth.curr_user)):
    """ 获取单个用户 """
    sql:str = f"SELECT * FROM {TABLE} WHERE id = %s AND deleted_at IS NULL"
    with Database() as cursor:
        cursor.execute(sql, (id,))
        user = cursor.fetchone()

    logger.info(f"user {name} get user {id}")
    result, msg = (True, "success") if user is not None else (False, "user not exists")
    return Response(user, result, msg)

@router.post('/users/insert')
def insert_user(user: UserCreate, name: str = Depends(Auth.curr_user)):
    fields: str = ','.join(f'"{k}"' for k in UserCreate.model_fields.keys())
    values: str = ','.join(f'%({k})s' for k in UserCreate.model_fields.keys())
    sql: str = f"INSERT INTO {TABLE} ({fields}) VALUES ({values})"
    count: int = 0
    with Database() as cur:
        cur.execute(sql, user.model_dump())
        count = cur.rowcount
    
    logger.info(f"user {name} insert user {user.username}")
    if count == 1:
        return Response(1)
    else:
        return Response(count, False, f"insert user {user.username} failed")

@router.post('/users/update/{id}')
def update_user(id: int, user: UserUpdate, name: str = Depends(Auth.curr_user)):
    updates: str = ",".join(f'"{k}" = %({k})s' for k in UserUpdate.model_fields.keys())
    user.updated_at = datetime.now()
    sql: str = f"UPDATE {TABLE} SET {updates} WHERE id = %(id)s AND deleted_at IS NULL"
    count: int = 0

    with Database() as cursor:
        cursor.execute(sql, {**user.model_dump(), "id": id})
        count = cursor.rowcount
    
    logger.info(f"user {name} update user {id}")
    if count == 1:
        return Response(1)
    else:
        return Response(count, False, f"update user {user.username} failed")

@router.post("/users/delete/{id}")
def delete_user(id: int, name: str = Depends(Auth.curr_user)):
    """ 删除用户 """
    sql: str = f"UPDATE {TABLE} SET deleted_at = %s WHERE id = %s"
    with Database() as cur:
        cur.execute(sql, (datetime.now(), id))
        count: int = cur.rowcount
    
    logger.info(f"user {name} delete user {id}")
    if count == 1:
        return Response(1)
    else:
        return Response(count, False, f"delete user {id} failed")
    