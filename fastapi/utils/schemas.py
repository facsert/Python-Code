from typing import Optional

from pydantic import BaseModel, Field


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
