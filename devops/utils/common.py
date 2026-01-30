""" common method """
import socket
from os import walk
from os.path import dirname, exists, join
from platform import system
from time import sleep
from pathlib import Path, PurePosixPath, PureWindowsPath

from loguru import logger


def title(msg: str="title", level:int=3, length: int=100) -> str:
    """ 标题打印 """
    index, msg = int(level) % 4, f" {msg} "
    logger.info(("\n\n", "\n", "", "")[index])
    border = ("#", "=", "*", "-")[index]
    logger.info(f" {msg:{border}^{length}}")
    return msg


def display(msg: str="checkpoint", success: bool=True) -> str:
    """ 结果打印 """
    if bool(success):
        logger.info(f"{msg:<80} [SUCCESS]")
    else:
        logger.error(f"{msg:><80} [FAILED]")
    return msg


def abs_dir(*path: str, platform: str=system().lower()) -> str:
    """ 以项目根路径作为相对路径基准拼接
    Param path str      : 相对路径或绝对路径
    Param platform str  : 根据平台变更拼接方式(linux, windows)
    Attention: 参数 path 相对路径必须相对于项目根目录
    """
    match platform.lower():
        case 'windows'|'win'|'w': 
            return str(PureWindowsPath(Path(__file__).parent.parent, *path))
        case 'linux'|'lin'|'unix'|'l'|'u': 
            return str(PurePosixPath(Path(__file__).parent.parent, *path))
        case _: 
            return str(Path(Path(__file__).parent.parent, *path))

def wait(delay: int=1, length: int=80) -> int:
    """ 等待进度条 """
    use = 0
    while use < delay:
        block = int(round(length * use / delay))
        text = f"[{'#' * block + '-' * (length - block)}]"
        print(f"Please wait {delay}s {text} {delay - use:>4}s", end="\r")
        sleep(1)
        use += 1
    print(f"Please wait {delay}s [{'#' * (length)}] {delay - use:>4}s")
    return delay

def list_dir(path=".", ignore=None):
    """ 递归遍历路径下的所有文件 """
    if not exists(path):
        display(f"{path} not exist", False)
        return []

    ignore = ignore if ignore else lambda f: False
    for root, _, files in walk(path):
        for file in files:
            if not ignore(file):
                yield join(root, file)

def conn_port(host: str, port: int, timeout: int=3) -> bool:
    """ 检查端口是否可连接 """
    try:
        with socket.create_connection((host, port), timeout):
            return True
    except (socket.timeout, socket.error):
        return False

if __name__ == '__main__':
    pass
