from time import sleep
from pytz import timezone
from datetime import datetime, timedelta

from loguru import logger
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
# from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.triggers.cron import CronTrigger
from apscheduler.job import Job

DATABASE_URL = f"postgresql+psycopg://{db.user}:{db.password}@{db.host}:{db.port}/{db.dbname}"

class Schedule:
    """ schedule module """

    @classmethod
    def init(cls):
        """ set schedule timezone """
        cls.scheduler: BackgroundScheduler = BackgroundScheduler(
            jobstores={
                # 'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
                'default': SQLAlchemyJobStore(url=DATABASE_URL)
                # 'default': MemoryJobStore()
            },
            executors={
                'default': ThreadPoolExecutor(20),    # 最大 default 执行器线程数 20
                'processpool': ProcessPoolExecutor(5) # processpoll 执行器最大线程数
            },
            job_defaults={
                'coalesce': False,  
                'max_instances': 3  # 最多并行实例
            },
            timezone=timezone("Asia/Shanghai")
        )
        cls.scheduler.start()

    @classmethod
    def get_jobs(cls):
        """ 获取 job 列表 """
        return cls.scheduler.get_jobs()

    @classmethod
    def get_job(cls, id: str):
        """ 获取 job 列表 """
        return cls.scheduler.get_job(id)

    @classmethod
    def add_once_job(cls, id: str, func: callable, params: dict|None, time: str, msg:str="") -> tuple[str, Job|None]:
        """ 添加 1 次性任务 """
        if cls.scheduler.get_job(id):
            return f"{id} already exists, rename the task", False
        
        try:
            time: datetime = datetime.fromisoformat(time)
        except Exception as err:
            return f"{time} format error: {err}", None
        
        cls.scheduler.add_job(func, 'date', kwargs=params, run_date=time, id=id)
        if job := cls.scheduler.get_job(id):
            return "success", job
        else:
            return "create task failed", None

    @classmethod
    def add_cron_job(cls, id: str, func: callable, params:None|dict, time: str, msg:str="")-> tuple[str, Job|None]:
        """ 添加 cron 类型任务 """
        if cls.scheduler.get_job(id):
            return f"{id} already exists, rename the task", False
        try:
            cls.scheduler.add_job(func, trigger=CronTrigger.from_crontab(time), kwargs=params, id=id, replace_existing=True)
        except Exception as err:
            return f"trigger time error: {err}", None
        
        if job := cls.scheduler.get_job(id):
            return "success", job
        else:
            return "create task failed", None

    @classmethod
    def remove(cls, id: str):
        """ 删除任务 """
        job: Job|None = cls.scheduler.get_job(id)
        if job is None:
            return f"{id} not exist", False

        job.remove()
        if cls.scheduler.get_job(id) is None:
            return f"remove {id} success", True
        else:
            return f"remove {id} failed", False
    
    @classmethod
    def pause(cls, id: str):
        job: Job|None = cls.scheduler.get_job(id)
        if  job is None:
            return f"{id} not exist", False
        
        if job.next_run_time is None:
            return f"{id} already paused", True
        
        if cls.scheduler.pause_job(id).next_run_time is not None:
            return f"pause {id} failed", False
        else:
            return f"pause {id} success", True

    @classmethod
    def resume(cls, id: str):
        job: Job|None = cls.scheduler.get_job(id)
        if  job is None:
            return f"{id} not exist", False
        
        if job.next_run_time is not None:
            return f"{id} is running", True

        if cls.scheduler.resume_job(id).next_run_time is None:
            return f"resume {id} failed", False
        else:
            return f"resume {id} success", True

    @classmethod
    def parse(cls, job: Job):
        return {"id": job.id, 'msg': job.name, "job": job.func.__name__, "next": job.next_run_time}

if __name__ == '__main__':
    once_task = lambda: print(f"task run at {datetime.now()}")
    once_task.__name__ = f"run once_task at {datetime.now()}"
    Schedule.add_once_job(id="once_task", func=once_task, timestamp=str(datetime.now() + timedelta(hours=3)))
