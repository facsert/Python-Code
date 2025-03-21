from dataclasses import dataclass
from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder as json_encode
from loguru import logger

from service.board import Board
from utils.database import Database


router = APIRouter()
TABLE = "boards"

@dataclass
class Response:
    content: any = None
    result: bool = True
    msg: str = "success"

@router.get('/boards')
def get_boards() -> JSONResponse:
    """ 获取所有单板 """
    with Database() as cursor:
        cursor.execute(f'SELECT * FROM {TABLE} WHERE deleted = false')
        boards = cursor.fetchall()
    return json_encode(Response(boards))

@router.get('/boards/{id}')
def get_board(id: int) -> JSONResponse:
    """ 获取所有节点列表 """
    with Database() as cursor:
        cursor.execute(f"SELECT * FROM {TABLE} WHERE id = '{id}' AND deleted = false")
        board = cursor.fetchone()

    result, msg = (True, "success") if board is not None else (False, f"board not exists")
    return json_encode(Response(board, result, msg))

@router.post('/boards/insert')
def insert_board(board: Board):
    fields: str = ','.join(f'"{k}"' for k in Board.model_fields.keys())
    values: str = ','.join(f'%({k})s' for k in Board.model_fields.keys())
    sql: str = f"""INSERT INTO {TABLE} ({fields}) VALUES ({values})"""
    count: int = 0
    with Database() as cur:
        cur.execute(sql, board.model_dump())
        count = cur.rowcount
    result, msg = (True, "success") if count == 1 else (False, f"insert board {board.number} failed")
    return json_encode(Response(count, result, msg))

@router.post('/boards/update/{id}')
def update_board(id: int, board: Board):
    updates: str = ",".join(f'"{k}" = %({k})s' for k in Board.model_fields.keys())
    sql: str = f"""UPDATE {TABLE} SET {updates} WHERE id = {id} AND deleted = false"""
    board.updated_at = str(datetime.now())
    count: int = 0

    with Database(dbname="postgres") as cursor:
        cursor.execute(sql, board.model_dump())
        count = cursor.rowcount
    result, msg = (True, "success") if count == 1 else (False, f"board {board.number} not exists")
    return json_encode(Response(count, result, msg))

@router.post("/boards/delete/{id}")
def delete_board(id: int):
    count:int = 0
    with Database(dbname="postgres") as cursor:
        cursor.execute(f"""
            UPDATE {TABLE} SET
            deleted = true, 
            updated_at = '{datetime.now()}' 
            WHERE id = {id} AND deleted = false
        """)
        count = cursor.rowcount

    result, msg = (True, "success") if count == 1 else (False, f"board {id} not exists")
    return json_encode(Response(count, result, msg))


