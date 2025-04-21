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
    content: any = None
    result: bool = True
    msg: str = "success"
    code: int = 200


class User(BaseModel):
    """user model"""

    id: int = Field(default=0, description="User ID")
    username: str = Field(max_length=50, description="Username")
    password: str = Field(max_length=100, description="Password")
    role: str = Field(default="guest", description="User role")
    created_at: datetime = Field(default=datetime.now(), description="Created at")
    updated_at: datetime = Field(default=datetime.now(), description="Updated at")
    deleted: bool = Field(default=False, description="Deleted")

class Node(BaseModel):
    """ node model """
    name: str = Field(description="node type name")
    host: str = Field(description="node host")
    port: int = Field(description="node ssh port")
    username: str = Field(description="node ssh username")
    password: str = Field(description="node ssh passward")
    version: Optional[str] = Field(default="v1", description="node version")
    description: Optional[str] = Field(default="node", description="node description")

class NodeUpdate(BaseModel):
    """ update node model """
    name: None|str = Field(default=None, description="node name")
    host: None|str = Field(default=None, description="node host")
    port: None|int = Field(default=None, description="node port")
    username: None|str = Field(default=None, description="node ssh username")
    password: None|str = Field(default=None, description="node ssh passward")
    version: None|str = Field(default=None, description="node RTS version")
    description: None|str = Field(default=None, description="node description")
