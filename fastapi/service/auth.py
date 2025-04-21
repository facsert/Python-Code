from datetime import datetime, timedelta
from os import getenv

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from utils.database import Database
from utils.schemas import User

JWT_SECRET = getenv("JWT_SECRET", "1b29df7aedc24d5d89aa36e4f352773c")


class Auth:
    """ Auth 服务 """
    
    secret_key: str = JWT_SECRET
    algorithm: str = 'HS256'

    def init(cls):
        pass

    @classmethod
    def create_token(cls, data: dict, expires_hours:int=24) -> str:
        """
        Create a token
        """
        expire: float = (datetime.now() + timedelta(hours=expires_hours)).timestamp()
        return jwt.encode(
            payload={**data, "exp": expire},
            key=cls.secret_key, 
            algorithm=cls.algorithm
        )
        
    @classmethod
    def decode_token(cls, token: str) -> dict:
        """
        Decode a token
        token 过期自动触发 jwt.ExpiredSignatureError
        """
        try:
            payload = jwt.decode(token, key=cls.secret_key, algorithms=[cls.algorithm])
            return payload, "success", True
        except jwt.ExpiredSignatureError:
            return {}, "token expired", False
    
        except jwt.InvalidTokenError:
            return {}, "token invalid", False

    @classmethod
    def check_password(cls, username: str, password: str) -> tuple[str, dict|None]:
        """
        Get user by username
        """
        user: dict|None = None
        with Database() as cur:
            cur.execute("SELECT * FROM users WHERE username = %s and deleted = false", (username,))
            user = cur.fetchone()
        
        if user is None:
            return f"username {username} not found", None
        
        if user['password'] != password:
            return "password error", None
        
        return "success", user

    @classmethod
    async def curr_user(cls, token: str=Depends(OAuth2PasswordBearer(tokenUrl="api/v1/auth/login"))):
        """
        Get current user by token
        """
        payload, msg, success = cls.decode_token(token)
        if not success:
            raise HTTPException(status_code=401, detail=msg, headers={"WWW-Authenticate": "Bearer"})

        return User(**payload)

if __name__ == '__main__':
    s = Auth.create_token({'id': 1, 'username': 'admin', 'password': '123456'})
    p = Auth.decode_token(s)[0]
    
    print(p)
    print(type(p))