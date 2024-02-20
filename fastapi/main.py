"""
description: fastapi 
"""
import sys
import socket
from os.path import dirname
from contextlib import asynccontextmanager

import uvicorn
from loguru import logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(dirname(__file__))
from utils.logger import logger_setting
from utils.router import add_routers

HOST = socket.gethostbyname(socket.gethostname()).strip()
PORT = 8001

@asynccontextmanager
async def lifespan(router: FastAPI):
    """ 应用开启和结束操作 """
    logger_setting()
    add_routers(router)
    logger.info("app start")
    yield
    logger.info("app close")

app = FastAPI(
    title="FastAPI",
    description=f"{HOST}:{PORT} api",
    version="0.0.1",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
