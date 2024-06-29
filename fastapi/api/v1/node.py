from datetime import datetime

from fastapi import APIRouter, Depends
from loguru import logger
from psycopg import Cursor

from utils import schemas
from utils.database import Nodes
from utils.database import Database


router = APIRouter()

def created():
    with Database.create_session() as session:
        yield session


@router.get('/nodes')
def get_nodes(session: Cursor = Depends(created)):
    """ 获取节点列表 """
    array = session.execute("select * from person").fetchall()
    logger.info(array)
    return array


@router.post('/nodes')
def add_nodes(node: schemas.NodeAdd, session: Cursor = Depends(created)):
    """ 获取节点列表 """
    node = node.model_dump()
    sql = "INSERT INTO person (name, age) VALUES(%(name)s, %(age)s);"
    cur = session.execute(sql, node)
    logger.info(f"Count:{cur.rowcount} Msg:{cur.statusmessage}")
    return cur.statusmessage

@router.get('/list')
def list_nodes():
    """ 获取节点列表 """
    nodes = list(Nodes.find({}))
    for n in nodes:
        n.pop('_id')
    return nodes


@router.put('/node')
def add_node(node: schemas.NodeAdd):
    """ 添加节点机器 """
    node_json = node.model_dump()
    now = datetime.now().strftime()
    node_json.update({
        'ssh': f'{node_json["host"]}:{node_json["port"]}',
        'create_time': now,
        'update_time': now,
    })
    node = Nodes.find_one({'ssh': node_json['ssh']})
    if node is not None:
        node.pop('_id')
        return node

    Nodes.insert_one(node_json)
    node = Nodes.find_one({'ssh': node_json['ssh']})
    node.pop('_id')
    return node


@router.delete('/node')
def delete_node_by_ssh(ssh: str):
    """ 按 ssh 删除节点 """
    return Nodes.delete_one({'ssh': ssh}).deleted_count

@router.post('/node')
def update_node_by_ssh(ssh: str, node: schemas.NodeUpdate):
    """ 按 ssh 更新节点信息 """
    logger.info("update")
    node = {k:v for k, v in node.model_dump().items() if v is not None}
    exist_node = Nodes.find_one({'ssh': ssh})
    if  exist_node is None:
        return None

    host, port = node.get('host', exist_node['host']), node.get('port', exist_node['port'])
    node['ssh'] = f"{host}:{port}"
    Nodes.update_one({'ssh': ssh}, {'$set': {**node, 'update_time': datetime.now().strftime()}})
    exist_node = Nodes.find_one({'ssh': ssh})
    exist_node.pop('_id')
    return exist_node


@router.post('/update_all')
def update_node_by_key(items: dict, node: schemas.NodeUpdate):
    """ 按匹配内容更新多个节点信息 """
    logger.info("update")
    node = {k:v for k, v in node.model_dump().items() if v is not None}
    if {'ssh', 'host', 'port'} <= set(node.keys()):
        return "ssh, host, port is unchangeable"
    
    exist_nodes = Nodes.find(items)
    if exist_nodes is None:
        return None
    
    Nodes.update_many(items, {'$set': {**node, 'update_time': datetime.now().strftime()}})
    
    exists = []
    exist_nodes = Nodes.find(items)
    for n in exist_nodes:
        n.pop('_id')
        exists.append(n)
    return exists


@router.get('/node')
def query_node_by_ssh(ssh: str):
    """ 按 ssh 查询节点 """
    node = Nodes.find_one({'ssh': ssh})
    node.pop('_id')
    return node

@router.post('/nodes')
def query_node_by_key(node: schemas.NodeUpdate):
    """ 按属性查询节点 """

    exists = []
    exist_nodes = Nodes.find({k:v for k, v in node.model_dump().items() if v is not None})
    if exist_nodes is None:
        return []
    
    for n in exist_nodes:
        n.pop('_id')
        exists.append(n)
    return exists
