from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from fastapi.encoders import jsonable_encoder as json_encode
from pydantic import BaseModel, Field


class JsonMeta(type):
    def __call__(cls, *args, **kwargs):
        return json_encode(super().__call__(*args, **kwargs))


@dataclass
class Response(metaclass=JsonMeta):
    """ response model """
    data: any = None
    result: bool = True
    msg: str = "success"
    code: int = 200

class UserLogin(BaseModel):
    """user model"""
    email: str = Field(description="User email")
    username: str = Field(max_length=50, description="Username")
    password: str = Field(max_length=100, description="Password")

class UserCreate(BaseModel):
    """user model"""
    email: str = Field(description="User email")
    username: str = Field(max_length=50, description="Username")
    password: str = Field(max_length=100, description="Password")

class UserUpdate(BaseModel):
    """user model"""
    email: str = Field(description="User email")
    username: str = Field(max_length=50, description="Username")
    password: str = Field(max_length=100, description="Password")
    updated_at: datetime = Field(description="Updated at")

class User(BaseModel):
    """user model"""
    __tablename__ = "users"

    id: int = Field(default=0, description="User ID")
    username: str = Field(max_length=50, description="Username")
    password: str = Field(max_length=100, description="Password")
    email: str = Field(description="User email")
    created_at: datetime = Field(description="Created at")
    updated_at: datetime = Field(description="Updated at")
    deleted_at: Optional[datetime] = Field(default=None, description="Deleted at")


if __name__ == "__main__":
    pass
