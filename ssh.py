'''
Author: facsert
Date: 2023-08-23 20:34:57
LastEditTime: 2023-08-28 21:54:41
LastEditors: facsert
Description: 
'''

import socket
from time import time, sleep
from textwrap import dedent
from paramiko import SSHClient, AutoAddPolicy

class Client:

    def __init__(self, host, port, username, password, timeout=30):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.client = self.connect()
        self.channel = self.client.invoke_shell()

    def __repr__(self) -> str:
        return dedent(f"""
            host    : {self.host}
            port    : {self.port}
            username: {self.username}
            password: {self.password}
            timeout : {self.timeout}
        """)

    def connect(self):
        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(
            self.host, 
            self.port, 
            self.username, 
            self.password, 
            timeout=self.timeout
        )
        return client

    def exec(self, command, timeout=5, view=True):
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
        print(command) if view else False
        _, stdout, _ = self.client.exec_command(command, timeout=timeout)
        stdout.channel.set_combine_stderr(True)

        succ, output, end_time = False, [], time() + timeout
        stdout.SEEK_END
        try:
            for line in stdout:
                if line == "" and stdout.channel.exit_status_ready():
                    succ = stdout.channel.recv_exit_status() == 0
                    break

                output.append(line)
                print(line, end="") if view else False

                if timeout > 0 and time() > end_time:
                    raise socket.timeout()
        except socket.timeout as e:
            err_msg = f"\nTimeoutError: {command}; \nReason: {e}"
            print(err_msg) if view else False
            output.append(err_msg)
    
        return succ, "".join(output)
    

    def shell(self, command, expect="", timeout=20, resp_timeout=3, view=True):
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
        print(command) if view else False
        self.channel.settimeout(timeout) 
        self.channel.sendall(command + '\n')
        resp_timeout = min(timeout, resp_timeout)

        buff, output, resp, last_time = "", '', 0, time() + timeout
        while True:
            if self.channel.recv_ready():
                data, buff = f"{buff}{self.channel.recv(65535).decode('utf-8')}", ""
                lines, output = data.splitlines(True), f"{output}{data}"
                resp, buff, lines = 0, lines[-1], ([], lines[:-1])[view]
                [print(line, end="", flush=True) for line in lines]
            else:
                sleep(0.1)
                resp += 0.1
                if resp > resp_timeout:
                    break
            
            end_time = (last_time + resp_timeout, last_time)[resp == 0]
            if time() > end_time:
                print(f"TimeoutError: {command}") if view else False
                output += f"\nTimeoutError: {command}"
                break

        return expect in output, output


    def sftp(self):
        return self.client.open_sftps()
        

if __name__ == "__main__":
    client = Client("192.168.1.103", 22, "root", "admin")
    print(client)
    # success, output = client.exec("ls -al", 3)
    # success, output = client.exec("cat -n /Users/facsert/.zshrc", 5)
    # succ, output = client.exec("data; sleep 5;date", 3)
    # print(succ)
    # success, output = client.exec("ping -c 5 localhost", 8)
    # success, output = client.exec("python3", 4)


    # print(output)
    # success, output = client.shell("ping -c 5 localhost", "127.0.0.1", 15)
    # succ, output = client.shell("python3")
    # succ, output = client.shell("a = 'hello'")
    # succ, output = client.shell("print(a)")
    # succ, output = client.shell("exit()")
    # succ, output = client.shell("cat << EOF")
    # succ, output = client.shell("A")
    # succ, output = client.shell("B")
    # succ, output = client.shell("EOF")
    # success, output = client.shell("top", "Aug", 5)
    # success, output = client.shell("top -n 4 -d 1 | grep %Cpu", 10)
    # print(output)
    # print(f"code: {succ}")     

