from traceback import format_exc

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger


def add_middlewares(app: FastAPI):
    """ 添加中间件 """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.middleware("http")
    async def catch_exceptions(request: Request, call_next):
        """ 捕获所有接口执行异常 """
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Error {type(e).__name__}: {e}")
            logger.error(format_exc())
            return JSONResponse(status_code=500, content={"message": "Server run error"})
