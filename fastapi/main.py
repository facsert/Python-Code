"""
description: fastapi 
"""
from contextlib import asynccontextmanager

import uvicorn
from loguru import logger
from fastapi import FastAPI

from utils.logger import LOGGER
from utils.database import Database
from utils.middleware import add_middlewares
from utils.router import add_routers


HOST = "localhost"
PORT = 8001

@asynccontextmanager
async def lifespan(router: FastAPI):
    """ 应用开启和结束操作 """
    Database.init()
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

add_middlewares(app)

if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host=HOST,
        port=PORT,
        reload=False,
        log_config=LOGGER,
        use_colors=False
    )
