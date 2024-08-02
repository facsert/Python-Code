from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html

from api.v1 import node, schedule
from utils.common import abs_dir


def add_routers(app: FastAPI):
    """ app add router"""
    app.include_router(node.router, prefix="/api/v1", tags=["node"])
    app.include_router(schedule.router, prefix="/api/v1", tags=["schedule"])

    # 指定本地 swagger-ui/dist 路径, 挂载到 /static 路由
    # app.mount('/static', StaticFiles(directory=abs_dir("static", "swagger-ui", "dist")), name="static")
    # 指定 /static 路由中的 js 文件
    # @app.get("/", include_in_schema=False)
    # async def custom_swagger_ui_html():
    #     """ set local static swagger """
    #     return get_swagger_ui_html(
    #         openapi_url=app.openapi_url,
    #         title=app.title,
    #         oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
    #         swagger_js_url="/static/swagger-ui-bundle.js",
    #         swagger_css_url="/static/swagger-ui.css",
    #     )
