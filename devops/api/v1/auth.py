
from fastapi import APIRouter, Depends, HTTPException
from fastapi import Response as Resp
from loguru import logger
from fastapi.security import OAuth2PasswordRequestForm

from service.auth import Auth
from utils.database import Database
from utils.schemas import Response, User, UserLogin

router = APIRouter()
TABLE_USERS: str = "users"


@router.post("/auth/sign")
def sign_user(user: UserLogin, resp: Resp):
    """ sign """
    user.password = Auth.hash_password(user.password)
    sql: str = """
        INSERT INTO users (username, password, email) 
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING
        RETURNING id
    """
    count: int = 0
    with Database() as cur:
        cur.execute(sql, (user.username, user.password, user.email))
        count = cur.rowcount

    if count == 0:
        return Response(result=False, msg=f"user {user.username} already exists")

    expires_hours: int = 24
    token: str = Auth.create_token(user.username, expires_hours)    
    resp.set_cookie("Authorization", f"Bearer {token}", path="/", max_age=expires_hours * 3600, httponly=True)
    return Response({'token': token})
@router.post("/auth/login")
def login_user(user: UserLogin, resp: Resp):
    """ login """
    msg, u = Auth.get_user(user.username, user.password)
    if u is None:
        return Response(None, False, msg)

    expires_hours: int = 24
    token: str = Auth.create_token(u.username, expires_hours)
    resp.set_cookie("Authorization", f"Bearer {token}", path="/", max_age=expires_hours * 3600, httponly=True)
    return Response({'token': token})

@router.post("/auth/token")
def swagger_login(form: OAuth2PasswordRequestForm = Depends()):
    """ token """
    msg, user = Auth.get_user(form.username, Auth.hash_password(form.password))
    
    if user is None:
        raise HTTPException(status_code=401, detail=msg)
    
    logger.info(f"swagger {user.username} login success")
    return {'access_token': Auth.create_token(user.username), 'token_type': 'bearer'}

@router.post("/auth/logout")
def logout(resp: Resp):
    """ logout """
    resp.delete_cookie("Authorization")
    return Response(None)






