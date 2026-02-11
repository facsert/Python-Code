import socket
from time import time, sleep
from json import dumps, loads

from loguru import logger
from paramiko import SSHClient, AutoAddPolicy
from paramiko.channel import Channel
from paramiko.sftp_client import SFTPClient


class Client:
    """paramiko 远程操作 linux"""

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        timeout: int = 60,
        **kwargs,
    ):
        self.host: str = host
        self.port: int = int(port)
        self.username: str = username
        self.password: str = password
        self.timeout: int = int(timeout)

        self.client: SSHClient = self.connect()
        self.channel: Channel | None = None
        self.sftp: SFTPClient | None = None

    def __repr__(self) -> str:
        return dumps(vars(self), indent=4)

    def connect(self):
        """连接 linux"""
        client: SSHClient = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(
            self.host, self.port, self.username, self.password, timeout=self.timeout
        )
        return client

    def close(self):
        """关闭 ssh 连接和通道"""
        if self.channel and not self.channel.closed:
            self.channel.close()
        if self.sftp:
            self.sftp.close()
        if self.client:
            self.client.close()

    def exec(
        self, command: str, timeout: int = 5, view: bool = True, interval: float = 0.05
    ) -> tuple[str, bool]:
        """执行非交互式命令行(shell, powershell), 并实时打印
        Args:
            command (str): linux 命令
            timeout (int): 超时时间. Defaults to 5.
            view (bool): 是否打印输出. Defaults to True.
            interval(float): 扫描输出间隔
        Raises:
            socket.timeout: 超时错误
        Returns:
            output(str): 命令执行返回值
            success(bool): 命令执行状态码为 0 为 True, 否则为 False
        Attention:
            该函数每次执行都相当于重新打开一个命令行, 执行完退出命令行
            每次执行默认在用户根路径
        """
        view and logger.info(command)
        _, stdout, _ = self.client.exec_command(command, timeout=timeout)
        stdout.channel.set_combine_stderr(True)
        success, output, deadline = False, [], time() + timeout
        chunk: str = ""
        try:
            while True:
                if stdout.channel.recv_ready():
                    data: bytes = stdout.channel.recv(4096)
                    try:
                        text: str = data.decode("utf-8")
                    except UnicodeDecodeError:
                        text: str = data.decode("gbk")

                    output.append(text)
                    if view and len(text) > 0:
                        lines: list[str] = f"{chunk}{text}".splitlines()
                        [logger.info(line) for line in lines[:-1]]
                        chunk = lines[-1]

                if stdout.channel.exit_status_ready():
                    success = stdout.channel.recv_exit_status() == 0
                    break

                if timeout > 0 and time() > deadline:
                    raise socket.timeout()

                sleep(interval)
        except socket.timeout as err:
            logger.error(f"\nTimeoutError: {command}; \nReason: {err}")
        return "".join(output), success

    def run(
        self,
        command: str,
        expect: None | list[str] = None,
        errors: None | list[str] = None,
        resp_timeout: int = 3,
        timeout: int = 60,
        view: bool = True,
        interval: float = 0.05,
    ) -> tuple[str, bool]:
        """交互式命令执行
        Args:
            command (str): linux 命令
            expect (None|list[str]): 预期值列表
            errors  (None|list[str]): 异常值列表
            timeout (int, optional): 命令执行超时. Defaults to 60.
            resp_timeout (int, optional): 无输出超时. Defaults to 5.
            view (bool): 是否打印输出. Defaults to True.
        Returns:
            output str: 命令执行返回值
            success bool: 预期值在命令返回值中国
        Attention:
            执行函数类似打开单个命令行, 每次执行均在同一个命令行中执行
            resp_timeout 为无输出超时时间, 超时后认为命令执行完毕
        """
        if self.channel is None or self.channel.closed:
            self.channel = self.client.invoke_shell()

        self.channel.settimeout(timeout)
        self.channel.sendall(command + "\n")
        resp_timeout = min(timeout, resp_timeout)
        
        chunk_length: int = 0
        if bool(expect) is False:
            expect = []
        else:
            chunk_length: int = max(len(k) for k in expect)
            expect = set(expect)

        if bool(errors) is False:
            errors = []
        else:
            errors = set(errors)
            chunk_length = max(chunk_length, max(len(k) for k in errors))

        resp_cost, result, chunk = 0, False, ""
        output, deadline = [], time() + timeout
        while True:
            if not self.channel.recv_ready():
                sleep(interval)
                resp_cost += interval
                if resp_cost < resp_timeout:
                    continue
                else:
                    break

            resp_cost = 0
            data: bytes = self.channel.recv(4096)
            try:
                text: str = data.decode("utf-8")
            except UnicodeDecodeError:
                text: str = data.decode("gbk")

            output.append(text)
            if view and len(text) > 0:
                [logger.info(line) for line in text.splitlines()]
            
            # 截取上次接收内容结尾部分内容, 避免内容拆分找不到关键字
            if chunk:
                text = chunk + text
            
            if any(k in text for k in errors):
                result = True
                break

            if any(k in text for k in expect):
                result = True
                break

            chunk = text[-(chunk_length-1):]  

            if time() > deadline:
                _ = logger.error(f"TimeoutError: {command}") if view else False
                output.append(f"\nTimeoutError: {command}")
                break

        return "".join(output), result

    def set_env_var(self, name: str, value: str, view: bool = False) -> bool:
        """设置环境变量
        Params:
            name str : 变量名
            value str : 变量值
        Return:
            success bool: 环境变量设置成功
        Attention:
            前后打印环境变量值不同则判定环境变量设置成功
        """
        cmd = f'export {name}={value} && echo "success ${name}, code: $?" || echo "error, code: $?"'
        success, output = self.run(
            cmd, expect=["code: 0"], errors=["code: 1"], resp_timeout=2, view=view
        )
        if success:
            logger.info(f"set environment {name}:{value}")
        else:
            logger.error(f"set environment {name} to {value} fail: {output}")
        return success

    def chdir(self, path: str) -> bool:
        """变更通道当前目录
        Params:
            path str : client 端绝对路径
        Return:
            success bool: 切换成功
        """
        cmd: str = f'cd {path} && echo "success code: $?, $PWD" || echo "failed code: $?, $PWD"'
        success, output = self.run(
            cmd, expect=["code: 0"], errors=["code: 1"], resp_timeout=2, view=False
        )
        if success:
            logger.info(f"change dir to {path} success")
        else:
            logger.error(f"change dir to {path} fail: {output}")
        return success

    def kill_proc(self, name: str, retry: int = 5, view: bool = False) -> bool:
        """杀死进程
        Params:
            name  str: 进程名称
            retry int: 重试次数
            view  bool: 是否打印输出
        Return:
            success bool: 进程成功关闭
        Attention:
            通过进程名称杀死对应进程判定进程关闭
        """

        for _ in range(retry):
            self.exec(f"pidof {name} && kill -15 $(pidof {name})", view=view)
            success, _ = self.exec(f"pidof {name}", view=view)
            if not success:
                return True
        else:
            logger.error(f"kill process {name} fail")
            return False

    def update_json(self, file_path: str, items: dict) -> bool:
        """更新远端 json 文件
        Params:
            file_path str : client 端 json 文件绝对地址
            items dict: 更新键值对
        Return:
            success bool: 文件更新成功
        """
        if self.sftp is None:
            self.sftp = self.client.open_sftp()

        try:
            with self.sftp.open(file_path, "r") as f:
                origin = loads(f.read())
            with self.sftp.open(file_path, "w") as f:
                f.write(dumps({**origin, **items}, indent=4))
            return True
        except Exception as e:
            logger.error(f"update {file_path} failed: {e}")
            return False


if __name__ == "__main__":
    client = Client("192.168.1.100", 8888, "username", "password")
    client.run("top", resp_timeout=2, timeout=5)
