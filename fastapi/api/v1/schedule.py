from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field

from service.schedule import Schedule


router = APIRouter()

class Job(BaseModel):
    """ schedule job """
    comment: str|None = Field(default=None, title="schedule job name unique")
    command: str|None = Field(default=None, title="command")
    schedule: str| None = Field(default=None, title="job schedule")

@router.get("/jobs")
def get_jobs():
    """ 列出所有任务信息 """
    jobs = list(Schedule.get_jobs().values())
    return JSONResponse(status_code=200, content=jsonable_encoder(jobs))

@router.get("/jobs/{comment}")
def get_schedule(comment: str):
    """ 获取单个任务详细信息 """
    job = Schedule.get_job(comment)
    content, code = ({'msg': f"job {comment} exist" }, 500) if job is None else (job, 200)
    return JSONResponse(status_code=code, content=jsonable_encoder(content))

@router.post("/job")
def add_job(job: Job):
    """ 新增定时任务 """
    task = Schedule.add_job(job.comment, job.command, job.schedule)
    content, code = ({'msg': f"{job.comment} already exist" }, 500) if task is None else (task, 200)
    return JSONResponse(status_code=code, content=jsonable_encoder(content))

@router.put("/job")
def update_job(comment: str, job: Job):
    """ 修改任务 """
    task = Schedule.update_job(comment, job.comment, job.command, job.schedule)
    content, code = ({'msg': f"{job.comment} not exist" }, 500) if task is None else (task, 200)
    return JSONResponse(status_code=code, content=jsonable_encoder(content))

@router.put("/job/{comment}/disable")
def disable_job(comment: str):
    """ 暂停定时任务 """
    job = Schedule.disable_job(comment)
    content, code = ({'msg': f"{comment} not exist" }, 500) if job is None else (job, 200)
    return JSONResponse(status_code=code, content=jsonable_encoder(content))

@router.put("/job/{comment}/enable")
def enable_job(comment: str):
    """ 恢复定时任务 """
    job = Schedule.enable_job(comment)
    content, code = ({'msg': f"{comment} not exist" }, 500) if job is None else (job, 200)
    return JSONResponse(status_code=code, content=jsonable_encoder(content))

@router.delete("/job")
def remove_job(comment: str):
    """ 删除任务 """
    job = Schedule.remove_job(comment)
    content, code = ({'msg': f"{comment} not exist" }, 500) if job is None else (job, 200)
    return JSONResponse(status_code=code, content=jsonable_encoder(content))
