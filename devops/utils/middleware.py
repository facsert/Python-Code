from traceback import format_exc

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from utils.schemas import Response


def add_middlewares(app: FastAPI):
    """ 添加中间件 """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition"],
    )

    @app.middleware("http")
    def catch_exceptions(request: Request, call_next):
        """ 捕获所有接口执行异常 """
        try:
            return call_next(request)
        except Exception as err:
            logger.error(f"Error {type(err).__name__}: {err}")
            logger.error(format_exc())
            return Response(
                data=None,
                result=False,
                msg=f"server error {type(err).__name__}: {err}",
                code=500
            )

            # token: str = request.cookies.get("token", "")
            # logger.info(dir(request.headers))
            # if token:
            #     headers = [*list(request.scope['headers']), ('Authorization', f'Bearer {token}')]
            #     request = Request(scope={**request.scope, 'headers': headers}, receive=request.receive)
            #     # request.headers["Authorization"] = f"Bearer {token}"
            #     # request.headers.__dict__["_list"].append(f"Bearer {token}")
            # logger.info(f"request headers: {request.headers.get('Authorization', 'empty')}")
