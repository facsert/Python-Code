""" common method """
from time import sleep
from platform import system
from os import walk
from os.path import join, dirname, exists

from loguru import logger


def title(msg: str="title", level:int=3, length: int=50) -> str:
    """ 标题打印 """
    index = int(level) % 3
    logger.info(("\n\n", "\n", "", "")[index])
    border = ("#", "=", "*", "-")[index] * length
    logger.info(f"{border} {msg} {border}")
    return msg


def display(msg: str="checkpoint", success: bool=True) -> str:
    """ 结果打印 """
    if bool(success):
        logger.info(f"{msg:<80} [PASS]")
    else:
        logger.error(f"{msg:><80} [FAIL]")
    return msg


def abs_dir(*path: str, platform: str|None =None) -> str:
    """ 以项目根路径作为相对路径基准拼接
    Param path str      : 相对路径或绝对路径
    Param platform str  : 根据平台变更拼接方式(linux, windows)
    Attention: 参数 path 相对路径必须相对于项目根目录
    """
    platform = system() if platform is None else platform
    abs_path = join(dirname(dirname(__file__)), join("", *path))
    sep = {'linux': '/', 'windows': '\\'}.get(platform.lower(), '/')
    return abs_path.replace("/", sep).replace("\\", sep)

def wait(delay: int=1, length: int=50) -> int:
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

def listdir(path=".", ignore=None):
    """ 递归遍历路径下的所有文件 """
    if not exists(path):
        display(f"{path} not exist", False)
        return []

    ignore = ignore if ignore else lambda f: False
    for root, _, files in walk(path):
        for file in files:
            if not ignore(file):
                yield join(root, file)


if __name__ == '__main__':
    wait(10)
    print(abs_dir("root/Desktop", "Python", platform="linux"))
