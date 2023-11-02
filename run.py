'''
Author: facsert
Date: 2023-08-07 20:44:56
LastEditTime: 2023-10-27 22:06:24
LastEditors: facsert
'''

from time import time, sleep
from select import select
from subprocess import Popen, PIPE, STDOUT
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK

def run(command, view=True, timeout=0):
    '''
    Description: 执行 linux 命令, 实时打印输出
    Param  command str : 执行的 shell 指令
    Param  view    bool: 是否显示执行过程
    Param  timeout int : 执行的 shell 指令超时时间
    Return code    int : 命令执行执行成功与否 
           output  str : 命令返回结果
    Attention: 
        若 timeout 设置 0 表示一直等到命令执行结束
    '''
    proc = Popen(
        command,
        shell=True, 
        stdout=PIPE, 
        stderr=STDOUT,
        text=True,
        bufsize=1
    )
    
    print(command) if view else False
    succ, line, output = False, "", []
    end_time = time() + timeout
    
    while True:
        readable, _, _ = select([proc.stdout], [], [], 0.1)
        if readable:
            line = proc.stdout.readline()
            if line != '':
                print(line, end='') if view else False
                output.append(line)
        
        if line == '' and proc.poll() is not None:
            succ = int(proc.poll()) == 0
            break

        if timeout > 0 and time() > end_time:
            output.append(f"\nTimeourError: {command}")
            break
        
    return succ, "".join(output)


class Terminal:

    def __init__(self, cmd='bash'):
        self.proc = Popen([cmd], stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True, shell=True, bufsize=1)
        self.pid = self.proc.pid

    def non_block_read(self, stdout):
        fd = stdout.fileno()
        fl = fcntl(fd, F_GETFL)
        fcntl(fd, F_SETFL, fl | O_NONBLOCK)
        try:
            return stdout.read()
        except Exception as _:
            return None
        
    def close(self):
        self.proc.terminate()

    def run(self, cmd, expect=None, resp_timeout=3, timeout=3, view=True):
        print(cmd)
        self.proc.stdin.write(f"{cmd}\n")
        self.proc.stdin.flush()
        resp_timeout = min(resp_timeout, timeout)
        succ, output, resp, last_time = False, "", 0, time() + timeout
        
        while True:
            data = self.non_block_read(self.proc.stdout)
            if data is not None:
                print(data, end='')
                output = f"{output}{data}"
                if expect is not None and expect in data:
                    succ, resp = True, resp_timeout
                else:
                    resp = 0
            else:
                sleep(0.1)
                resp += 0.1
            if resp >= resp_timeout:
                break

            end_time = (last_time + resp_timeout, last_time)[resp == 0]
            if time() > end_time:
                print(f"TimeoutError: {cmd}") if view else False
                output = f"{output}\nTimeoutError: {cmd}"
                break
            
        return succ, "".join(output)

if __name__ == '__main__':
    t = Terminal()
    t.run("export name=petter")
    t.run('echo "name: $name"')
