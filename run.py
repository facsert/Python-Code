'''
Author: facsert
Date: 2023-08-07 20:44:56
LastEditTime: 2023-08-07 21:36:33
LastEditors: facsert
Description: 
'''

from subprocess import Popen, PIPE, STDOUT

def run(command):
    '''
    Description: 执行 linux 命令, 实时打印输出
    Param command str: 执行的 shell 指令 
    Return output str code int: 命令执行结果, 命令执行代码(判断执行结果) 
    Attention: 
    '''

    process = Popen(
        command, 
        shell=True, 
        stdout=PIPE, 
        stderr=STDOUT, 
        text=True
    )
    
    print(command)
    output = ""
    while True:
        line = process.stdout.readline()
        if line == '' and process.poll() is not None:
            break

        output += line
        print(line, end='')

    return output, process.poll()

if __name__ == '__main__':
    content, code = run("ping -c 3 localhost")
    print(content, code)
