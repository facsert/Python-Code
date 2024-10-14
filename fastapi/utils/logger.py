"""
description: 
"""
import sys
import logging
from datetime import timedelta

from loguru import logger
# from uvicorn.config import LOGGING_CONFIG

from utils.common import abs_dir

LOG_PATH = abs_dir('log', 'report.log')
ROTATION_DAY: int = 7
RETENTION_DAY: int = 30
LOG_FORMAT: str = '[<green>{time:YYYY-MM-DD HH:mm:ss}</green>][<level>{level: <8}</level>]: <level>{message}</level>'

class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentaion.
    """

    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def logger_init():
    """
    拦截 uvicorn 输出, 使用 loguru 接管
    """
    logging.getLogger("uvicorn.asgi").handlers = [InterceptHandler()]
    logging.getLogger("uvicorn").handlers = [InterceptHandler()]
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]

    logger.remove()
    logger.add(sys.stderr,  level='INFO', format=LOG_FORMAT)
    logger.add(
        LOG_PATH,
        level='INFO',
        format=LOG_FORMAT,
        rotation=timedelta(days=ROTATION_DAY),
        retention=timedelta(days=RETENTION_DAY),
        enqueue=True
    )


# uvicorn 日志重新配置
# LOGGER = LOGGING_CONFIG
# LOGGER["formatters"]["default"]['format'] = "[%(asctime)s][%(levelname)-8s]: %(message)s"
# LOGGER["formatters"]["default"]['datefmt'] = "%Y-%m-%d %H:%M:%S"
# LOGGER["handlers"]["default_file"] = {"formatter": "default", "class": "logging.FileHandler", "filename": LOG_PATH}
# LOGGER["loggers"]["uvicorn"]["handlers"].append("default_file")

# LOGGER["formatters"]["access"]['format'] = "[%(asctime)s][%(levelname)-8s]: %(client_addr)s %(request_line)s %(status_code)s"
# LOGGER["formatters"]["access"]['datefmt'] = "%Y-%m-%d %H:%M:%S"
# LOGGER["handlers"]["access_file"] = {"formatter": "access", "class": "logging.FileHandler", "filename": LOG_PATH}
# LOGGER["loggers"]["uvicorn.access"]["handlers"].append("access_file")