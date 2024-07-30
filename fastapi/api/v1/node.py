from fastapi import APIRouter
from loguru import logger

from utils import schemas
from utils.database import Database


router = APIRouter()

@router.get('/nodes')
def get_nodes():
    """ 获取节点列表 """
    with Database() as cursor:
        array = cursor.execute("select * from node").fetchall()
    logger.info(array)
    return array


@router.post('/nodes')
def add_nodes(node: schemas.Node):
    """ 获取节点列表 """
    node = node.model_dump()
    sql = "INSERT INTO node (host, port) VALUES (%(host)s, %(port)s);"
    with Database as cursor:
        cursor.execute(sql, node)
    logger.info(f"Count:{cursor.rowcount} Msg:{cursor.statusmessage}")
    return cursor.statusmessage
