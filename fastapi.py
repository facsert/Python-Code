"""
Author: facsert
Date: 2023-10-23 20:24:32
LastEditTime: 2023-10-23 20:24:33
LastEditors: facsert
Description: 
"""

import uvicorn
from fastapi import FastAPI
from os.path import join, dirname
from os import getcwd
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)


app = FastAPI()
app.mount(                                       # 挂载静态文件, 路由 /static 和本地 swagger-ui 文件夹 对应
    '/static',                                   # /static -> ./static/swagger-ui/dist
    StaticFiles(directory=join(getcwd(), 'static', 'swagger-ui', 'dist')),
    name="static"
)

app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],  
      allow_credentials=True,
      allow_methods=["*"],  
      allow_headers=["*"],  
)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

@app.get("/")
async def root():
    return "root page"

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)