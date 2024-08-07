import socket
from time import time, sleep
from json import dumps, load

from loguru import logger
from paramiko import SSHClient, AutoAddPolicy
from paramiko.channel import Channel
from paramiko.sftp_client import SFTPClient


class Client:
    """ paramiko 远程操作 linxu """

    def __init__(self, host: str, port: int, username: str, password: str, timeout: int=60):
        self.host: str = host
        self.port: int = int(port)
        self.username: str = username
        self.password: str = password
        self.timeout: int = int(timeout)

        self.client: SSHClient = self.connect()
        self.channel: Channel = self.client.invoke_shell()
        self.sftp: SFTPClient = self.client.open_sftp()

    def __repr__(self) -> str:
        return dumps(vars(self), indent=4)

    def connect(self):
        """ 连接 linux """
        client: SSHClient = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(
            self.host,
            self.port,
            self.username,
            self.password,
            timeout=self.timeout
        )
        return client

    def close(self):
        """ 关闭 ssh 连接和通道 """
        _ = self.channel.close() if self.channel else None
        _ = self.client.close() if self.client else None

    def exec(self, command: str, timeout: int=5, view: bool=True) -> tuple[bool, str]:
        """执行非交互式 linux 命令, 并实时打印

        Args:
            command (str): linux 命令
            timeout (int, optional): 超时时间. Defaults to 5.

        Raises:
            socket.timeout: 超时错误

        Returns:
            succ bool: 命令执行成功或失败
            output str: 命令执行返回值

        Attention:
            
        """
        _ = logger.info(command) if view else False
        _, stdout, _ = self.client.exec_command(command, timeout=timeout)
        stdout.channel.set_combine_stderr(True)
        succ, output, end_time = False, [], time() + timeout
        try:
            while True:
                line = stdout.readline()
                if line == "" and stdout.channel.exit_status_ready():
                    succ = stdout.channel.recv_exit_status() == 0
                    break

                output.append(line)
                _ = logger.info(line.rstrip()) if view else False
                if timeout > 0 and time() > end_time:
                    raise socket.timeout()
        except socket.timeout as e:
            err_msg = f"\nTimeoutError: {command}; \nReason: {e}"
            logger.error(err_msg)
            output.append(err_msg)
        return succ, "".join(output)

    def run(
        self,
        command: str,
        expect: None|list=None,
        resp_timeout: int=3,
        timeout: int=60,
        view: bool=True
    ) -> tuple[bool, str]:
        """交互式命令执行
        Args:
            command str: linux 命令
            expect  str: 预期值
            timeout (int, optional): 命令执行超时. Defaults to 20.
            resp_timeout (int, optional): 响应超时. Defaults to 5.

        Returns:
            succ bool: 预期值在命令返回值中国
            output str: 命令执行返回值

        Attention:
            管道无返回值开始计时到 resp_timeout 时间, 认为命令输出完毕
            若等待响应开始计时(resp > 0), 执行时间超过 timeout + resp_timeout 才算超时
            若命令一直有输出(响应计时 resp == 0), 执行 timeout 时间后退出
        """
        self.channel.settimeout(timeout)
        self.channel.sendall(command + '\n')
        resp_timeout = min(timeout, resp_timeout)

        expect_check, check_result = isinstance(expect, list), False
        buff, output, resp, end_time = "", [], 0, time() + timeout
        while True:
            if self.channel.recv_ready():
                data = f"{self.channel.recv(10).decode('utf-8', 'ignore')}"
                output.append(data)
                data = f"{buff}{data}"
                lines, resp = data.splitlines(True), 0
                buff, lines = ("", lines) if data.endswith('\n') else (lines[-1], lines[:-1])

                for line in lines:
                    _ = logger.info(line.rstrip()) if view else False
                    if expect_check and any(k in line for k in expect):
                        resp, check_result = resp_timeout, True
            else:
                sleep(0.1)
                resp += 0.1
                if resp > resp_timeout:
                    break

            if time() > end_time:
                _ = logger.error(f"TimeoutError: {command}") if view else False
                output.append(f"\nTimeoutError: {command}")
                break
        return check_result, output

    def set_env_var(self, variable: str, value: str, view: bool=False) -> bool:
        """ 设置环境变量
        Params:
            variable str : linux 命令
            value    str : 命令返回预期值

        Return:
            succ bool: 环境变量设置成功

        Attention:
            前后打印环境变量值不同则判定环境变量设置成功
        """
        cmd = f'export {variable}={value}; echo "${variable}, code: $?"'
        succ, output = self.run(cmd, "code: 0", resp_timeout=2, view=view)

        if succ:
            logger.info(f"set environment {variable}:{value}")
        else:
            logger.error(f"set environment {variable} to {value} fail")
        return succ

    def chdir(self, path: str) -> bool:
        """ 变更通道当前目录
        Params:
            dir str : client 端绝对路径

        Return:
            succ bool: 切换成功
        """
        cmd: str = f'cd {path}; echo $PWD, code: $?'
        succ, output = self.run(cmd, "code: 0", resp_timeout=2, view=False)
        if succ:
            logger.info(f"change dir to {path}")
        else:
            logger.error(f"change dir to {path} fail: {output}")
        return succ

    def kill_proc(self, key: str, view: bool=False, retry: int=30) -> bool:
        """ 杀死进程
        Params:
            key   str: 进程关键字
            retry int: 重试次数

        Return:
            succ bool: 进程成功关闭

        Attention:
            通过关键字查询不到对应进程判定进程关闭
        """

        check: str = f"ps -eaf | grep -E {key} | grep -v grep"
        kill: str = check + "|awk '{print $2}' | xargs kill -15"
        father_kill: str = check + "|awk '{print $3}' | xargs kill -15"
        while retry:
            proc_alive, _ = self.exec(check, timeout=10, view=view)
            self.exec((kill, father_kill)[retry < 5], timeout=10, view=view)
            if proc_alive:
                sleep(0.1)
                retry -= 1
                continue
            break
        return retry > 0

    def update_json(self, file: str, items: dict) -> bool:
        """ 更新远端 json 文件
        Params:
            file  str : client 端 json 文件绝对地址
            items dict: 更新键值对

        Return:
            succ bool: 文件更新成功
        """
        try:
            with self.sftp.open(file, 'r') as f:
                origin = load(f)
            with self.sftp.open(file, 'w') as f:
                f.write(dumps({**origin, **items}, indent=4))
        except Exception as e:
            logger.error(f"update {file} failed: {e}")
        return True


if __name__ == "__main__":
    client = Client("10.121.238.42", 10205, "root", "EcsAdmin?")
    client.run("top", resp_timeout=2, timeout=5)
