import asyncio
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
    
    first, task = True, None
    async def send():
        while True:
            logger.info(f"log timestamp: {datetime.now()}")
            await websocket.send_text(f"timestamp: {datetime.now()}")
            await asyncio.sleep(2)

    while True:
        data = await websocket.receive_text()
        if 'start' in data and first:
            task = asyncio.create_task(send())
            first = False

        logger.info(f"Received data: {data}")
        if data == "exit":
            _ = task.cancel() if task else None
            break
    
    await websocket.close()
        