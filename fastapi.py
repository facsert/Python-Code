"""
Author: facsert
Date: 2023-10-23 20:24:32
LastEditTime: 2023-10-23 20:24:33
LastEditors: facsert
Description: 
"""

from fastapi import FastAPI
from fastapi.middleware.core import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)