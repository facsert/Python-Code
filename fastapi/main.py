"""
description: fastapi 
"""
from contextlib import asynccontextmanager

import uvicorn
from loguru import logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from utils.logger import logger_setting
from utils.router import add_routers
from utils.db import Database
from utils.middleware import add_middlewares

HOST = "localhost"
PORT = 8001

@asynccontextmanager
async def lifespan(router: FastAPI):
    """ 应用开启和结束操作 """
    logger_setting()
    Database.init()
    add_routers(router)
    logger.info("app start")
    yield
    logger.info("app close")
    Database.close()

app = FastAPI(
    title="FastAPI",
    description=f"{HOST}:{PORT} api",
    version="0.0.1",
    lifespan=lifespan
)

add_middlewares(app)


if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
