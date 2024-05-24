import socket
from json import load
from os.path import join, isabs, dirname
from platform import system

from loguru import logger

def abs_dir(*path, os=""):
    """ 获取文件或目录的绝对路径
    Param path str  : 相对路径或绝对路径
    Param os   str  : 根据 os 变更路径格式
    Return succ bool: 绝对路径文件或路径是否存在
           abs str  : 绝对路径
    Attention: 参数 path 相对路径必须相对于 pytest 根目录(run.py 同级目录)
    """
    platform = system() if platform is None else platform
    abs_path = join(dirname(dirname(__file__)), join("", *path))
    sep = {'linux': '/', 'windows': '\\'}.get(platform.lower(), '/')
    return abs_path.replace("/", sep).replace("\\", sep)


def json_load(path):
    """ 解析 json 文件返回字典
    Param  path   str : 相对路径或绝对路径
    Return succ   bool: 解析成功或失败
           config dict: 字典
    Attention: 解析失败, 返回一个包含 error 原因的字典
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return load(f)
    except Exception as e:
        return {"error": f"Read {path} error: {e}"}


def title(msg='title', level=3, length=50):
    """根据 level 等级打印不同样式的标题

    Args:
        msg (str): 标题内容. Defaults to 'title'.
        level  (int): 标题等级 (0, 1, 2, 3). Defaults to 3.
        length (int): 标题两端符号的数量. Defaults to 30.

    Returns:
        None: 无返回值

    Attention:
        标题有4个等级, 与符号对应关系是
            0: '#'
            1: '='
            2: '*'
            3: '-'
    """
    try:
        logger.info(("\n\n", "\n", "", "")[level])
        border = ('#', '=', '*', '-')[level] * length
        logger.info(f'{border} {msg} {border}')
    except IndexError as _:
        logger.error(f'IndexError: level 0~3, but use {level}')

    return msg


def display(msg="checkpoint", succ=True):
    """ 打印阶段性结果
    Param msg str: 显示内容
    succ  bool| None: 检查结果
    Example:
        True:  checkpoint                     [PASS] (显示 pass 结果)
        False: checkpoint>>>>>>>>>>>>>>>>>>>>>[FAIL] (显示 fail 结果)
        None:  checkpoint>>>>>>>>>>>>>>>>>>>>>[FAIL] (显示 fail 结果并退出)
    """
    if succ is True:
        logger.info(f'\33[32m{msg:<100} [SUCC] \33[37m')
    else:
        logger.error(f'\33[31m{msg:><100} [FAIL] \33[37m')
    return msg


def socket_port(host, port):
    """ 检查端口是否可用
    Param host str: 主机地址
    Param port int: 端口
    Return succ bool: 端口是否可用
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect((host, int(port)))
            return True
    except Exception as e:
        logger.error(f'Check port {port} error: {e}')
        return False
    finally:
        s.close()

if __name__ == "__main__":
    pass
