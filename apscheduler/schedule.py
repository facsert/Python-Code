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


class Schedule:
    """ schedule module """

    scheduler: BackgroundScheduler | None = None
    jobstores = {
        # 'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
        'default': MemoryJobStore()
    }
    executors = {
        'default': ThreadPoolExecutor(20),
        'processpool': ProcessPoolExecutor(5)
    }
    job_defaults = {
        'coalesce': False,
        'max_instances': 3
    }

    @classmethod
    def init(cls):
        """ set schedule timezone """
        cls.scheduler = BackgroundScheduler(
            jobstores=cls.jobstores,
            executors=cls.executors,
            job_defaults=cls.job_defaults,
            timezone=timezone("Asia/Shanghai")
        )
        cls.scheduler.start()

    @classmethod
    def get_jobs(cls):
        """ get all jobs """
        return cls.scheduler.get_jobs()

    @classmethod
    def add_once_job(cls, id: str, func: callable, timestamp: datetime):
        """ create once job """
        cls.scheduler.add_job(func, 'date', run_date=timestamp, id=id)

    @classmethod
    def add_cron_job(cls, id: str, func: callable, cron: str):
        """ create crontab job """
        cls.scheduler.add_job(func, trigger=CronTrigger.from_crontab(cron), id=id)

    @classmethod
    def remove_job(cls, id: str):
        """ remove job """
        cls.scheduler.remove_job(id)

    @classmethod
    def parse_job(cls, job: Job):
        """ parse job as dict """
        return {"id": job.id, "job": job.func.__name__, "next": job.next_run_time}

if __name__ == '__main__':
    once_task = lambda: print(f"task run at {datetime.now()}")
    once_task.__name__ = f"run once_task at {datetime.now()}"
    Schedule.add_once_job(id="once_task", func=once_task, timestamp=datetime.now() + timedelta(hours=3))
