'''
Author: facsert
Date: 2023-08-07 20:44:56
LastEditTime: 2023-10-27 21:58:20
LastEditors: facsert
Description: 
'''

from time import time, sleep
from select import select
from subprocess import Popen, PIPE, STDOUT


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

if __name__ == '__main__':
    pass

