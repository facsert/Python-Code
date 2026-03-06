"""set script args"""

from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from dataclasses import asdict, dataclass, fields
from datetime import datetime
from os.path import basename
from textwrap import dedent

@dataclass
class Param:
    dest: str                # args 对象的属性名称
    flags: list[str]         # 参数使用方式
    help: str = "help info"  # 参数帮助信息
    action: str = "store"    # 参数行为 (store_true store_false 不能设置 type 和 choices)
    default: str | int = ""  # 默认值
    required: bool = False   # 参数是否必须
    choices: any = None      # 参数可选值, [1, 2, 3] 表示参数仅允许为 1,2,3


params: list[Param] = [
    Param(
        dest="dir",
        flags=["-d", "--dir"],
        help="set csv dir",
        action="store",
        default="/root",
        required=True,
    ),
    Param(
        dest="output",
        flags=["-o", "--output"],
        help="set output",
        action="store",
        default="",
        required=False,
    ),
    Param(
        dest="prefix",
        flags=["-p", "--prefix"],
        help="set output file prefix",
        action="store",
    ),
]


# 自定义帮助信息
HELP = dedent("""

Get script help info
    python script.py --help

Set log path
    python script.py --dir /root/home

Set csv output
    python script.py --output /root/csv

Set csv filename prefix
    python script.py --prefix log

example
    python script.py --dir /root/home --output /root/csv --prefix 2026-03-04
""")


@dataclass
class Flag:
    dir: str
    output: str
    prefix: str

class Arg:
    """脚本参数解析"""

    def __new__(cls, params: list[Param]=params, help: str=HELP) -> Flag:
        cls.params: list[Param] = params
        cls.help: str = help
        cls.flag: Flag|None = None
        return cls.main()
    
    @classmethod
    def parse(cls):
        """ 解析命令行参数 """
        parse = ArgumentParser(
            description="Usage",
            formatter_class=RawDescriptionHelpFormatter,
        )

        parse.epilog = cls.help
        parse.add_argument("--version", "-v", action="version", version="1.0.0")

        for param in cls.params:
            d: dict = asdict(param)
            flags: list[str] = d.pop("flags")
            parse.add_argument(*flags, **d)

        space: Namespace = parse.parse_args()
        cls.flag = Flag(**{f.name: getattr(space, f.name) for f in fields(Flag)})
    
    @classmethod
    def init(cls):
        """ 参数初始化 """
        if cls.flag.dir == "":
            cls.flag.dir = "/root"
        
        if cls.flag.output == "":
            cls.flag.output = cls.flag.dir

        if cls.flag.prefix == "":
            cls.flag.prefix = (
                f"{datetime.now().strftime('%Y%m%d')}_{basename(cls.flag.dir)}_"
            )

    @classmethod
    def main(cls) -> Flag:
        """创建参数解析对象"""
        cls.parse()
        cls.init()
        return cls.flag

if __name__ == "__main__":
    flag = Arg()
    print(flag)
