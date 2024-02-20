"""
description: 
"""
import sys

from loguru import logger

from lib.common import abs_dir

def logger_setting():
    """ 设置 logger """
    logger.remove()

    fmt = '[<level>{level: <8}</level>][<green>{time:YYYY-MM-DD HH:mm:ss}</green>]: <level>{message}</level>'
    logger.add(sys.stderr,  level='INFO', format=fmt)
    logger.add(abs_dir('log', 'report.log'),
        level='INFO', format=fmt, rotation='1 week', retention='30 days'
    )

    logger.level("HTTP", no=36)
    logger.add(abs_dir('log', 'http.log'),
        level='HTTP', format=fmt,
        filter=lambda r: r['level'].no == 36,
        rotation='1 week', retention='30 days'
    )
