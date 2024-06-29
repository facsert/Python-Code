"""
description: 
"""
import sys

from loguru import logger
from uvicorn.config import LOGGING_CONFIG

from lib.common import abs_dir


LOG_PATH = abs_dir('log', 'report.log')

# uvicorn 日志重新配置
LOGGER = LOGGING_CONFIG
LOGGER["formatters"]["default"]['format'] = "[%(asctime)s][%(levelname)-8s]: %(message)s"
LOGGER["formatters"]["default"]['datefmt'] = "%Y-%m-%d %H:%M:%S"
LOGGER["handlers"]["default_file"] = {"formatter": "default", "class": "logging.FileHandler", "filename": LOG_PATH}
LOGGER["loggers"]["uvicorn"]["handlers"].append("default_file")

LOGGER["formatters"]["access"]['format'] = "[%(asctime)s][%(levelname)-8s]: %(client_addr)s %(request_line)s %(status_code)s"
LOGGER["formatters"]["access"]['datefmt'] = "%Y-%m-%d %H:%M:%S"
LOGGER["handlers"]["access_file"] = {"formatter": "access", "class": "logging.FileHandler", "filename": LOG_PATH}
LOGGER["loggers"]["uvicorn.access"]["handlers"].append("access_file")


logger.remove()
fmt = '[<green>{time:YYYY-MM-DD HH:mm:ss}</green>][<level>{level: <8}</level>]: <level>{message}</level>'
logger.add(sys.stderr,  level='INFO', format=fmt)
logger.add(abs_dir('log', 'report.log'),
    level='INFO', format=fmt, rotation='50 MB', retention='30 days'
)
