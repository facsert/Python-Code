'''
Author: facsert
Date: 2023-08-07 20:44:56
LastEditTime: 2023-08-24 23:05:38
LastEditors: facsert
Description: 
'''

import asyncio
from time import time
from select import select
from subprocess import Popen, PIPE, STDOUT


def run(command, timeout=30):
    '''
    Description: 执行 linux 命令, 实时打印输出
    Param command str: 执行的 shell 指令
    Param timeout int: 执行的 shell 指令超时时间
    Return code int: 命令执行执行成功与否 
           output str: 命令返回结果
    Attention: 
    '''

    proc = Popen(
        command, 
        shell=True, 
        stdout=PIPE, 
        stderr=STDOUT, 
        text=True,
        bufsize=1
    )
    
    print(command)
    succ, line, output = False, "", ""
    end_time = time() + timeout
    
    while True:
        readable, _, _ = select([proc.stdout], [], [], 0.1)
        if readable:
            line = proc.stdout.readline()
            if line != '':
                print(line, end='')
                output += line
        
        if line == '' and proc.poll() is not None:
            succ = int(proc.poll()) == 0
            break

        if time() > end_time:
            output += f"\nTimeourError: {command}"
            break
        
    return succ, output

if __name__ == '__main__':
    # succ, output = run("top -n 5 -d 1 -b | grep %Cpu", 30)
    succ, output = run("ping -c 5 localhost", 30)
    succ, output = run("sleep 2;date", 30)
    # print(output)
