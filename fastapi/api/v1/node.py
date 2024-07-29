from datetime import datetime

from fastapi import APIRouter, Depends
from loguru import logger
from psycopg import Cursor

from utils import schemas
from utils.database import Nodes
from utils.database import Database


router = APIRouter()

@router.get('/nodes')
def get_nodes():
    """ 获取节点列表 """
    with Database() as cursor:
        array = cursor.execute("select * from person").fetchall()
    logger.info(array)
    return array


@router.post('/nodes')
def add_nodes(node: schemas.NodeAdd):
    """ 获取节点列表 """
    node = node.model_dump()
    sql = "INSERT INTO person (name, age) VALUES(%(name)s, %(age)s);"
    with Database as cursor:
        cursor.execute(sql, node)
    logger.info(f"Count:{cursor.rowcount} Msg:{cursor.statusmessage}")
    return cursor.statusmessage
