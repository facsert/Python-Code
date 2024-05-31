from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import jwt

from utils.database import Database
# from jose import JWTError, jwt

import jwt
from uuid import uuid4
from datetime import datetime, timedelta


# Token 模型
class Token(BaseModel):
    sub: str
    exp: float
    

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = uuid4().hex
ALGORITHM = 'HS256'
EXPIRE_HOURS = 24

class Jwt:
    """ Jwt 服务 
    用户登录后，签发 token
    """
    
    @classmethod
    def authentication(cls, username: str, password: str):
        user = Database.get_session().execute("SELECT password FROM users WHERE username = %s", (username)).fetchone()
        return user.get("password") == password
            
    @classmethod
    def create_token(cls, data: dict, expires_hours:int=0) -> str:
        """
        Create a token
        
        """
        hours: int = EXPIRE_HOURS if expires_hours == 0 else expires_hours
        expire: float = (datetime.now() + timedelta(hours=hours)).timestamp()
        return jwt.encode(payload={**data, "exp": expire}, key=SECRET_KEY, algorithm=ALGORITHM)
        
    @classmethod
    def decode_token(cls, token: str) -> dict:
        """
        Decode a token
        token 过期自动触发 jwt.ExpiredSignatureError
        """
        try:
            return jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM]), True
        except jwt.ExpiredSignatureError:
            return {"status": 401, "msg": "Token expired", "expire": True}, False
        except jwt.InvalidTokenError:
            return {"status": 401, "msg": "Token invalid", "invalid": True}, False

def raise_exception(status_code: int=status.HTTP_401_UNAUTHORIZED, detail: str=""):
    raise HTTPException(
        status_code=status_code,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )

async def authentication(token: str = Depends(oauth2_scheme)):

    try:
        data:dict = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise_exception(detail="Token expired")
    except jwt.InvalidTokenError:
        raise_exception(detail="Token invalid")
 
    if data.get("username", None):
        raise_exception(detail="Token invalid")
        
    username, password = data.get("username"), data.get("password")
    user = Database.get_session().execute("SELECT password FROM users WHERE username = %s", (username)).fetchone()
    
    if user is None:
        raise_exception(detail="Username invalid")
    
    if password != user.get("password"):
        raise_exception(detail="Password invalid")   
        
    return data

async def permission(data: str = Depends(authentication), permission_key=None) -> dict:
    """ 权限验证 """
    if permission_key is None:
        return data
    
    if data.get(permission_key, False) is False:
        raise_exception(detail="Permission denied")
        
    return data
