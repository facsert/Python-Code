from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from loguru import logger
from psycopg import Cursor

from utils import schemas
from utils.database import Database
from utils.common import title, display


router = APIRouter()
TABLE = "node"

def connect():
    """ connect database, close after leave """
    with Database() as cursor:
        yield cursor

@router.get('/nodes')
def get_nodes(cur: Cursor = Depends(connect)) -> JSONResponse:
    """ 获取所有节点列表 """
    sql: str = f"SELECT * FROM {TABLE}"
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({'data': cur.execute(sql).fetchall(), 'result': True})
    )

@router.get('/nodes/{name}')
def get_node(name: str, cursor: Cursor = Depends(connect)) -> JSONResponse:
    """ 按 name 查询节点 """
    sql = f"SELECT * FROM {TABLE} WHERE name = %s"
    node = cursor.execute(sql, (name,)).fetchone()
    if node is not None:
        code, content = 200, {'data': node, 'result': True}
    else:
        code, content = 500, {'data': f"{name} not in Database", 'result': False}
    return JSONResponse(status_code=code, content=jsonable_encoder(content))

@router.post('/node')
def add_node(node: schemas.Node, cursor: Cursor = Depends(connect))-> JSONResponse:
    """ 添加节点机器 """
    title(f"Add {node.name} {node.host}:{node.port}", 3)
    node_json = node.model_dump()
    logger.info(node_json)
    values = ",".join(f"%({k})s" for k in list(node_json))
    sql = f"""
        INSERT INTO {TABLE} ({','.join(list(node_json))}) VALUES ({values})
        ON CONFLICT (name, host, port) DO NOTHING
        RETURNING *
    """
    cursor.execute(sql, node_json)
    add = cursor.fetchone()
    if add is not None:
        code, content = 200, {'data': add, 'result': True}
    else:
        code, content = 500, {'data':f"{node.name} {node.host}:{node.port} exixts",'result':False}
    return JSONResponse(status_code=code, content=jsonable_encoder(content))

@router.delete('/node/{name}')
def delete_node(name: str, cursor: Cursor = Depends(connect))-> JSONResponse:
    """ 按 name 删除节点 """
    title(f"Delete {name}", 3)
    sql = f"DELETE FROM {TABLE} WHERE name = %s RETURNING *"
    node = cursor.execute(sql, (name,)).fetchone()
    if node is not None:
        code, content = 200, {'data': node, 'result': True}
    else:
        code, content = 500, {'data': f"{name} not in Database", 'result': False}
    return JSONResponse(status_code=code, content=jsonable_encoder(content))

@router.put('/node/{name}')
def update_node(
        name: str,
        node: schemas.NodeUpdate,
        cursor: Cursor = Depends(connect)
    ) -> JSONResponse:
    """ 按 name 更新节点信息 """
    title(f"Update {name}", 3)
    sql_get = f"SELECT id FROM {TABLE} WHERE name = %s"
    node_id = cursor.execute(sql_get, (name,)).fetchone()
    if node_id is None:
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder({'data': f"{name} not in database", 'result': False})
        )

    node_json = node.model_dump()
    logger.info(node_json)
    update_items = ",".join(f"{k} = %({k})s" for k, v in node_json.items() if bool(v))
    sql = f"""
        UPDATE {TABLE} SET {update_items}
        WHERE id = %(id)s
        RETURNING *;
    """
    update = cursor.execute(sql, {**node_json, 'id': node_id['id']}).fetchone()
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({'data': update, 'result': True})
    )
