from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder as json_encode
from loguru import logger
from fastapi.security import OAuth2PasswordRequestForm

from service.auth import Auth
from utils.database import Database
from utils.schemas import Response, User

router = APIRouter()
TABLE_USERS: str = "users"

@router.post("/auth/login")
def token_login(form: OAuth2PasswordRequestForm = Depends()):
    """ 用户登录, 返回 token """
    logger.info(f"login user: {form.username}")
    msg, user = Auth.check_password(form.username, form.password)

    if user is None:
        raise HTTPException(status_code=401, detail=msg)
    
    logger.info(f"login user: {form.username} success")
    return {'access_token': Auth.create_token(json_encode(user)), 'token_type': 'bearer', **user}

@router.get("/auth/users")
def get_users(user: User = Depends(Auth.curr_user)):
    with Database() as cur:
        cur.execute(f"SELECT * FROM {TABLE_USERS} WHERE deleted = false")
        users: list[User] = cur.fetchall()
    logger.info(f"get users: {user}")
    return Response(content=users)

@router.get("/auth/users/{id}")
def get_user(id: int):
    user: User|None = None
    with Database() as cur:
        cur.execute(f"SELECT * FROM {TABLE_USERS} WHERE id = %s AND deleted = false", (id,))
        user: User = cur.fetchone()

    if user is None:
        return Response(result=False, msg=f"user {id} not found")

    return Response(user)

@router.post("/auth/register")
def register(user: User):
    insert: str = """
        INSERT INTO users (username, password) 
        VALUES (%s, %s)
        ON CONFLICT (username, deleted) DO NOTHING
        RETURNING id
    """
    count: int = 0
    with Database() as cur:
        cur.execute(insert, (user.username, user.password))
        count = cur.rowcount

    if count == 0:
        return Response(result=False, msg=f"user {user.username} already exists")

    return Response(msg="register success")

@router.post("/auth/logout")
def logout(user: User):
    return Response(content=None)

@router.post("/auth/delete/{id}")
def delete_user(id: int):
    with Database() as cur:
        cur.execute(f"UPDATE {TABLE_USERS} SET deleted = true WHERE id = {id}")
        count: int = cur.rowcount
    
    if count == 0:
        return Response(result=False, msg=f"user {id} not found")
    
    return Response(msg="delete success")

@router.put("/auth/update/{id}")
def update_user(id: int, user: User):
    update: str = f"""
        UPDATE {TABLE_USERS} SET username = %s, password = %s, updated_at = %s
        WHERE id = %s AND deleted = false
        RETURNING id
    """
    count: int = 0
    with Database() as cur:
        cur.execute(update, (user.username, user.password, datetime.now(), id))
        count = cur.rowcount
    
    if count == 0:
        return Response(result=False, msg=f"user {id} not found")
    
    return Response(msg="update success")





