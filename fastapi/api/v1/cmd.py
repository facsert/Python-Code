from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from loguru import logger

# from utils.database import Database
from utils.common import title, display


router = APIRouter()

@router.websocket("/ws")
async def run_cmd(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        if data == "exit":
            await websocket.close()
            break
        await websocket.send_text(f"Enter data: {data} with timestamp: {datetime.now()}")