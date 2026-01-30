"""
description: fastapi 
"""
import os
from contextlib import asynccontextmanager

import uvicorn
from loguru import logger
from fastapi import FastAPI

from utils.logger import logger_init
from utils.router import add_routers
from utils.database import Database
from utils.middleware import add_middlewares

HOST = '0.0.0.0'
PORT = 8000
PID = os.getpid()

@asynccontextmanager
async def lifespan(router: FastAPI):
    """ 应用开启和结束操作 """
    logger_init()
    logger.info(f"Server {HOST}:{PORT} process {PID} start")
    add_routers(router)
    Database.init()
    yield
    logger.info(f"Server {HOST}:{PORT} process {PID} close")

app = FastAPI(
    title="FastAPI",
    description=f"{HOST}:{PORT} api",
    version="0.0.1",
    lifespan=lifespan
)

add_middlewares(app)

if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host=HOST,
        port=PORT,
        reload=False,
        use_colors=False
    )
