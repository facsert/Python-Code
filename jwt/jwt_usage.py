import jwt
from uuid import uuid4
from datetime import datetime, timedelta


class Jwt:
    """ Jwt 服务 """
    
    secret_key: str = uuid4().hex
    algorithm: str = 'HS256'
    expires_hours: int = 1
    
    @classmethod
    def create_token(cls, data: dict, expires_hours:int=0) -> str:
        """
        Create a token
        """
        hours: int = cls.expires_hours if expires_hours == 0 else expires_hours
        expire: float = (datetime.now() + timedelta(hours=hours)).timestamp()
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
            return jwt.decode(token, key=cls.secret_key, algorithms=[cls.algorithm]), True
        except jwt.ExpiredSignatureError:
            return {"status": 401, "msg": "token expired", "expire": True}, False
        except jwt.InvalidTokenError:
            return {"status": 401, "msg": "token invalid", "invalid": True}, False
        
if __name__ == '__main__':
    from time import sleep
    token = Jwt.create_token({"id": 1, "username": "admin", "password": "root" })
    print(token)
    sleep(3)
    data, success = Jwt.decode_token(token)
    print(data)