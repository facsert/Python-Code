from typing import Optional

from pydantic import BaseModel, Field


class Node(BaseModel):
    """ node model """
    host: str = Field(description="node host")
    port: int = Field(description="node ssh port")
    name: str = Field(description="node type name")
    username: str = Field(description="node ssh username")
    password: str = Field(description="node ssh passward")
    version: Optional[str] = Field(default="v1", description="node version")
    description: Optional[str] = Field(default="node", description="node description")
