from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html

from api.v1 import node
from lib.common import abs_dir


def add_routers(app: FastAPI):
    """ app add router"""
    app.include_router(node.router, prefix="/node", tags=["node"])

    app.mount('/static', StaticFiles(directory=abs_dir("static", "swagger-ui", "dist")), name="static")
    @app.get("/", include_in_schema=False)
    async def custom_swagger_ui_html():
        """ set local static swagger """
        return get_swagger_ui_html(openapi_url=app.openapi_url, title=app.title,)
