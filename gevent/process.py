'''
Author: facsert
Date: 2023-08-07 20:44:56
LastEditTime: 2023-10-27 22:06:24
LastEditors: facsert
'''

from time import time

import gevent
import gevent.subprocess
from gevent import Timeout
from loguru import  logger


class Process:
    """ 使用 gevent 无阻塞执行命令 """

    def __init__(self):
        self.proc = None

    @staticmethod
    def exec(command: str, timeout: int=30, view: bool=True) -> tuple[bool, str]:
        """ 
        Description: 非交互式命令执行
            Param  command str : 执行的 shell 指令
            Param  timeout int : 执行的 shell 指令超时时间
            Param  view    bool: 是否显示执行过程

        Return 
            succ    bool : 命令执行执行成功与否 
            output  str : 命令返回结果

        Attention: 
            若 timeout 设置 None 表示一直等到命令执行结束
        """
        proc = gevent.subprocess.Popen(
            command,
            shell=True,
            stdout=gevent.subprocess.PIPE,
            stderr=gevent.subprocess.STDOUT,
            text=True,
        )

        logger.info(command)
        succ, line, output = False, "", []
        try:
            with Timeout(timeout, TimeoutError):
                while True:
                    line = proc.stdout.readline()
                    if line != "":
                        _ = logger.info(line.rstrip()) if view else False
                        output.append(line)

                    if line == "" and proc.poll() is not None:
                        succ = int(proc.poll()) == 0
                        break
        except TimeoutError:
            logger.error("TimeoutError")
            output.append(f"\nTimeourError: {command}")

        return succ, "".join(output)

    def create(self,
        command: str,
        expect: None|list=None,
        resp_timeout: int=5,
        timeout: int=30,
        view: bool=True
    ) -> tuple[bool, str]:
        """ 
        Description: 创建交互式命令 执行
            Param  command str : 执行指令字符串
            Param  expect str  : 命令输出期望, 输出行出现预期则退出
            Param  resp_timeout int : 执行命令无输出的超时时间
            Param  timeout int : 执行的 命令的超时时间
            Param  view    bool: 是否显示执行过程

        Return 
            succ    str : 输出是否包含 expect
            output  str : 命令返回结果
        """
        self.proc = gevent.subprocess.Popen(
            command,
            shell=True,
            stdin=gevent.subprocess.PIPE,
            stdout=gevent.subprocess.PIPE,
            stderr=gevent.subprocess.STDOUT,
            text=True,
        )
        logger.info(command)
        succ, output = self.read(expect, resp_timeout, timeout, view)
        return succ, output

    def close(self):
        """ 关闭进程 """
        _ = self.proc.kill() if self.proc else None

    def send(self,
        command: str,
        expect: None|list=None,
        resp_timeout: int=5,
        timeout: int=30,
        view: bool=True
    ):
        """ 
        Description: 交互式进程写入命令
            Param  command str : 写入管道的命令
            Param  expect str  : 命令输出期望, 输出行出现预期则退出
            Param  resp_timeout int : 执行命令无输出的超时时间
            Param  timeout int : 执行命令的超时时间
            Param  view    bool: 是否显示执行过程

        Return 
            succ    str : 输出是否包含 expect
            output  str : 命令返回结果  
        """
        logger.info(command)
        self.proc.stdin.write(f"{command}\n")
        self.proc.stdin.flush()
        succ, output = self.read(expect, resp_timeout, timeout, view)
        return succ, output

    def read(self,
        expect: None|list=None,
        resp_timeout: int=5,
        timeout: int=30,
        view: bool=True
    ):
        """ 
        Description: 读取交互式进程的输出
            Param  expect str  : 命令输出期望, 输出行出现预期则退出
            Param  resp_timeout int : 执行命令无输出的超时时间
            Param  timeout int : 执行命令的超时时间
            Param  view    bool: 是否显示执行过程

        Return 
            succ    str : 输出是否包含 expect
            output  str : 命令返回结果  
        """
        end = time() + timeout
        succ, line, output = False, "", []
        while True:
            try:
                with Timeout(resp_timeout, TimeoutError):
                    self.proc.stdout.flush()
                    line = self.proc.stdout.readline()
            except TimeoutError:
                logger.error("No Response TimeoutError")
                output.append("\nNo Response TimeoutError")
                break

            if line == "" and self.proc.poll() is not None:
                break

            if line != "":
                _ = logger.info(line.rstrip()) if view else False
                output.append(line)

                if isinstance(expect, list) and any(k in line for k in expect):
                    succ = True
                    break

            if time() >= end:
                logger.error("\nRun command timeout")
                output.append("\nRun Command TimeoutError")
                break
        return succ, "".join(output)

if __name__ == '__main__':
    Process.exec("ping -c 3 127.0.0.1")
