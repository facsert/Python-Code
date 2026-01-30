from hashlib import sha256
from datetime import datetime, timedelta
from os import getenv

import jwt
from fastapi import Depends, Request, HTTPException
from fastapi.security import OAuth2PasswordBearer
# from loguru import logger

from utils.database import Database
from utils.schemas import User, UserLogin

JWT_SECRET = getenv("JWT_SECRET", "1b29df7aedc24d5d89aa36e4f352773c")


# class OAuth2CookieBearer(OAuth2PasswordBearer):
    
#     async def __call__(self, request: Request) -> str|None:
#         token = request.headers.get("Authorization")
#         if token:
#             token = token.split(" ")[1] if " " in token else token
#         else:
#             token = request.cookies.get("token")

#         if not token:
#             if self.auto_error:
#                 raise HTTPException(
#                     status_code=401,
#                     detail="Not authenticated",
#                     headers={"WWW-Authenticate": "Bearer"},
#                 )
#             else:
#                 return None
#         return token

class Auth:
    """Auth 服务"""

    secret_key: str = JWT_SECRET
    algorithm: str = "HS256"

    @classmethod
    def create_token(cls, username: str, duration: int=24) -> str:
        """
        Create token
        """
        expire: float = (datetime.now() + timedelta(hours=duration)).timestamp()
        return jwt.encode(
            payload={"username": username, "exp": expire}, 
            key=cls.secret_key, 
            algorithm=cls.algorithm,
        )

    @classmethod
    def parse_token(cls, token: str) -> tuple[str, dict]:
        """
        Decode a token
        token 过期自动触发 jwt.ExpiredSignatureError
        """
        try:
            payload = jwt.decode(token, key=cls.secret_key, algorithms=[cls.algorithm])
            return "success", payload
        except jwt.ExpiredSignatureError:
            return "token expired", {}

        except jwt.InvalidTokenError:
            return "token invalid", {}
        
        except Exception as err:
            return f"parse token failed: {err}", {}
    
    @classmethod
    def hash_password(cls, password: str) -> str:
        hash = sha256()
        hash.update(password.encode("utf-8"))
        return hash.hexdigest()

    @classmethod
    def get_user(cls, username: str, password: str) -> tuple[str, User|None]:
        """
        Get user by username
        """
        user: dict | None = None
        with Database() as cur:
            cur.execute("""
                SELECT * FROM users 
                WHERE 
                    username = %s AND 
                    password = %s AND 
                    deleted_at is NULL
                """,
                (username, password),
            )
            user = cur.fetchone()

        if user is None:
            return "username or password error", None

        return "success", User(**user)
    

    @classmethod
    async def curr_user(
        cls, token: str=Depends(OAuth2PasswordBearer(tokenUrl="api/v1/auth/token"))
    ):
        """
        Get current user by token
        """
        msg, payload = cls.parse_token(token)
        if len(payload) == 0:
            raise HTTPException(
                status_code=401, 
                detail=msg, 
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload.get("username", "not exist")



if __name__ == "__main__":
    s = Auth.create_token({"id": 1, "username": "admin", "password": "123456"})
    p = Auth.parse_token(s)[0]

    print(p)
    print(type(p))
