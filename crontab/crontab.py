from datetime import datetime

from crontab import CronTab, CronItem, CronSlices

# pip install python-crontab
# pip install croniter

class Schedule:
    """ Crontab 定时任务 """

    @classmethod
    def init(cls):
        """ 对象初始化 """
        cls.cron: CronTab = CronTab(user="root")
        cls.jobs = {}
        cls.tasks = {}
        cls.refresh()

    @classmethod
    def refresh(cls):
        """ 刷新 """
        cls.jobs, cls.tasks = {}, {}
        for job in cls.cron:
            if bool(job.comment):
                cls.jobs[job.comment] = job
                cls.tasks[job.comment] = cls.json_job(job)

    @classmethod
    def json_job(cls, job: CronItem) -> dict:
        """ job 对象 json """
        schedule = job.schedule(date_from=datetime.now())
        return {
            'comment': job.comment,
            'command': job.command,
            'schedule': f"{job.minute} {job.hour} {job.dom} {job.month} {job.dow}",
            'prev': str(schedule.get_prev()),
            'next': str(schedule.get_next()),
            'enable': job.is_enabled(),
        }

    @classmethod
    def add_job(cls, comment: str, command: str, timestamp: str) -> dict|None:
        """ 添加定时任务 """
        if cls.tasks.get(comment):
            return f"{comment} exist", False

        if not CronSlices.is_valid(timestamp):
            return f"{timestamp} Invaild", False

        job: CronItem = cls.cron.new(command, comment)
        job.setall(timestamp)
        cls.cron.write()
        cls.refresh()
        return cls.tasks.get(comment), True


    @classmethod
    def get_jobs(cls) -> dict:
        """ 获取所有定时任务 """
        cls.refresh()
        return cls.tasks

    @classmethod
    def get_job(cls, comment: str) -> dict:
        """ 按 comment 获取 job """
        cls.refresh()
        return cls.tasks.get(comment, None)

    @classmethod
    def disable_job(cls, comment: str) -> bool:
        """ 暂停任务 """
        if cls.jobs.get(comment, None) is None:
            return False

        cls.jobs[comment].enable(False)
        cls.cron.write()
        cls.refresh()
        return True

    @classmethod
    def enable_job(cls, comment: str) -> bool:
        """ 恢复任务 """
        if cls.jobs.get(comment, None) is None:
            return False

        cls.jobs[comment].enable()
        cls.cron.write()
        cls.refresh()
        return True

    @classmethod
    def update_job(cls, comment_id: str, comment=None, command=None, timestamp=None):
        """ 更新任务 """
        job, task = cls.jobs.get(comment_id, None), cls.tasks.get(comment_id, None)
        if job is None or task is None:
            return None

        if comment_id != comment and bool(comment):
            job.set_comment(comment)

        if bool(command):
            job.set_command(command)

        if bool(timestamp):
            job.setall(timestamp)

        cls.cron.write()
        cls.refresh()
        return cls.tasks[comment]

    @classmethod
    def remove_job(cls, comment: str):
        """ 删除任务 """
        task = cls.jobs.get(comment, None)
        if task is None:
            return None

        cls.cron.remove(cls.jobs[comment])
        cls.cron.write()
        cls.refresh()
        return task

if __name__ == '__main__':
    from json import dumps
    Schedule.init()
    print(dumps(Schedule.get_jobs(), indent=4))