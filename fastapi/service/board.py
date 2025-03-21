from datetime import datetime

from pydantic import BaseModel, Field


class Board(BaseModel):
    """ board model """
    number: str = Field(description="board number")

    host: str = Field(description="board host")
    port: int = Field(description="board ssh port")
    username: str = Field(default="root", description="board ssh username")
    password: str = Field(default="EcsAdmin?", description="board ssh password")

    owner: str = Field(description="board msg")
    email: str = Field(description="board msg")
    msg: str = Field(default="RTS", description="board msg")
    created_at: datetime = Field(default=datetime.now(), deprecated="Board info created time")
    updated_at: datetime = Field(default=datetime.now(), deprecated="Board info last update time")
