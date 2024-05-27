# -*- coding: utf-8 -*-
'''
Author: facsert
Date: 2023-08-05 21:06:59
LastEditTime: 2023-08-29 21:38:04
LastEditors: facsert
Description: 
'''

from logging import (StreamHandler, FileHandler, Formatter, getLogger,
    NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL)

# logging 显示等级定义
# CRITICAL = 50
# FATAL = CRITICAL
# ERROR = 40
# WARNING = 30
# WARN = WARNING
# INFO = 20
# DEBUG = 10
# NOTSET = 0

class logger:
    """格式化打印内容
    
    Example:
        logger.info(str) 
        logger.error(str)
        
    Args:
        file:  打印内容重定向到的文件
        level: 显示等级
        format:打印格式
    """
    log = None
    red = '\033[91m'
    yellow = '\033[93m'
    reset = '\033[0m'
    date_format = "%Y-%m-%d %H:%M:%S"
    file_format = "[%(levelname)-5s][%(asctime)s]: %(message)s"
    terminal_format = "[%(levelname)-5s][%(asctime)s]: %(message)s"

    @classmethod
    def create_logger(cls, file="report.log", level="info"):
        '''
        Description: 删除原有的 handler, 创建新的命令行和文本 handler
        Param file str: log 输出文件
        Param level str: 显示 log 的等级
        Return: None
        Attention: 多个 logger 对象会重复输出
        '''
        cls.remove_handler()
        cls.log = getLogger('log')
        cls.level = cls.get_level(level)
        cls.handle_terminal(cls.level, cls.terminal_format, cls.date_format)
        cls.handle_file(file, cls.level, cls.file_format, cls.date_format)
        cls.log.setLevel(cls.level)

    @classmethod
    def remove_handler(cls):
        '''
        Description: 遍历 logger 对象, 移除 handler
        Return: None
        Attention: 
        '''
        if cls.log is None:
            return
        for handler in cls.log.handlers[:]:
            handler.close()
            cls.log.removeHandler(handler)

    @staticmethod
    def get_level(level):
        '''
        Description: 根据等级字符串获取等级
        Return int: 显示等级 
        Attention: 若非法 level, 默认返回 INFO 
        '''
        return {
            'NOTSET': NOTSET,
            'DEBUG': DEBUG,
            'INFO': INFO,
            'WARNING': WARNING,
            'ERROR': ERROR,
            'CRITICAL': CRITICAL,    
        }.get(level.upper(), INFO)

    @classmethod
    def handle_terminal(cls, level, format, datefmt):
        '''
        Description: 配置命令行打印控制器
        Param level str: 命令行显示 log 等级 
        Param format str: 命令行 log 打印前缀 
        Attention: 默认与全部使用设置显示等级, 可自定义
        '''
        handler = StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(Formatter(format, datefmt))
        cls.log.addHandler(handler)

    @classmethod
    def handle_file(cls, file, level, format, datefmt):
        '''
        Description: 配置文件打印控制器
        Param file str:  log 输出文件 
        Param level str: 文件记录 log 等级 
        Param format str: 文件 log 打印前缀 
        Attention: 默认与全部使用设置显示等级, 可自定义
        '''
        handler = FileHandler(file)
        handler.setLevel(level)
        handler.setFormatter(Formatter(format, datefmt))
        cls.log.addHandler(handler)

    @classmethod
    def info(cls, msg):
        '''
        Description: 打印 info log 
        Param msg str: 打印内容 
        Return msg str: 打印内容 
        Attention: 
        '''
        if cls.log is None:
            cls.create_logger()
        cls.log.info(msg)
        return msg

    @classmethod
    def error(cls, msg):
        '''
        Description: 打印 error log, 命令行显示为红色
        Param msg str: 打印内容 
        Return msg str: 打印内容 
        Attention: 
        '''
        if cls.log is None:
            cls.create_logger()
        cls.log.error(f'{cls.red}{msg}{cls.reset}')
        return msg

    @classmethod
    def debug(cls, msg):
        '''
        Description: 打印 debug log, 命令行显示为黄色
        Param msg str: 打印内容 
        Return msg str: 打印内容 
        Attention: 
        '''
        if cls.log is None:
            cls.create_logger()
        cls.log.debug(f'{cls.yellow}{msg}{cls.reset}')
        return msg
