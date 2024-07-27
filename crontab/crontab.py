from crontab import CronTab
from loguru import logger


class Schedule:
    """ Crontab 定时任务 """

    @classmethod
    def init(cls):
        """ 对象初始化 """
        logger.info("Schedule Init")
        cls.cron = CronTab(user="root")
        cls.jobs = {job.comment: job for job in cls.cron}
        cls.tasks = {job.comment: cls.json_job(job) for job in cls.cron}

    @classmethod
    def refresh(cls):
        """ 重新获取 crontab 任务 """
        cls.jobs = {job.comment: job for job in cls.cron}
        cls.tasks = {job.comment: cls.json_job(job) for job in cls.cron}

    @classmethod
    def json_job(cls, job) -> dict:
        """ job 对象 json """
        schedule = f"{job.minute} {job.hour} {job.dom} {job.month} {job.dow}"
        return {
            'comment': job.comment,
            'command': job.command,
            'schedule': schedule,
            'enable': job.is_enabled(),
        }

    @classmethod
    def add_job(cls, comment, command, timestamp) -> dict:
        """ 添加定时任务 """
        if cls.jobs.get(comment):
            return None

        job = cls.cron.new(command=command, comment=comment)
        job.setall(timestamp)
        cls.cron.write()
        cls.jobs[comment], cls.tasks[comment] = job, {'comment': comment, 'command': command, 'schedule': timestamp}
        return {'comment': comment, 'command': command, 'schedule': timestamp}

    @classmethod
    def get_jobs(cls):
        """ 获取所有定时任务 """
        cls.refresh()
        return cls.tasks

    @classmethod
    def get_job(cls, comment):
        """ 按 comment 获取 job """
        return cls.tasks.get(comment, None)

    @classmethod
    def disable_job(cls, comment):
        """ 暂停任务 """
        if cls.jobs.get(comment, None) is None:
            return None
        cls.jobs[comment].enable(False)
        cls.tasks[comment]['enable'] = False
        cls.cron.write()
        return cls.tasks[comment]

    @classmethod
    def enable_job(cls, comment):
        """ 恢复任务 """
        if cls.jobs.get(comment, None) is None:
            return None
        cls.jobs[comment].enable()
        cls.tasks[comment]['enable'] = True
        cls.cron.write()
        return cls.tasks[comment]

    @classmethod
    def update_job(cls, comment_id, comment=None, command=None, timestamp=None):
        """ 更新任务 """
        job, task = cls.jobs.get(comment_id, None), cls.tasks.get(comment_id, None)
        if job is None or task is None:
            return None

        if comment_id != comment:
            del cls.jobs[comment_id]
            del cls.tasks[comment_id]
            job.set_comment(comment)
            cls.jobs[comment], cls.tasks[comment] = job, task
            task['comment'] = comment

        if command is not None:
            job.set_command(command)
            task['command'] = command

        if timestamp is not None:
            job.setall(timestamp)
            task['schedule'] = timestamp
        cls.cron.write()
        return task

    @classmethod
    def remove_job(cls, comment):
        """ 删除任务 """
        task = cls.tasks.get(comment, None)
        if task is None:
            return None
        cls.cron.remove(cls.jobs[comment])
        del cls.jobs[comment]
        del cls.tasks[comment]
        cls.cron.write()
        return task

if __name__ == '__main__':
    pass
