""" set script args """
from textwrap import dedent
from argparse import ArgumentParser, RawDescriptionHelpFormatter


ARGS = [{
        'dest': 'exit',
        'flags': ['-e', '--exit'],
        'help': 'error exit',
        'action': 'store_true',
        'default': False,
    },{
        'dest': 'cycle',
        'flags': ['-c', '--cycle'],
        'help': 'run cycle times',
        'action': 'store',
        'type': int,
        'default': 1,
        'required': True,
    }
]

TEMPLATE = {
    "dest": "default",                           # args 对象的属性名称
    "flags": ['-f', '--flag'],                   # 参数使用方式
    "default": None,                             # 默认值
    "type": None,                                # 参数类型
    "action": "store",                           # 参数行为 (store_true store_false 不能设置 type 和 choices)           
    "choices": None,                             # 参数可选值, [1, 2, 3] 表示参数仅允许为 1,2,3
    "required": False,                           # 参数是否必须
    "help": "default help",                      # 参数帮助信息
}

# 自定义帮助信息
HELP = dedent('''
              
Get script help info
    python script.py --help

Get script version
    python script.py --version

run script
    python script.py
''')


class Arg:
    """ 脚本参数解析 """

    def __new__(cls):
        cls.args = ARGS
        cls.help = HELP
        return cls.main()

    @classmethod
    def main(cls):
        """ 创建参数解析对象 """
        parse = ArgumentParser(
            description='Usage',
            formatter_class=RawDescriptionHelpFormatter,
        )
        parse.add_argument(
            '--version', '-v', 
            action='version',
            version='1.0.0'
        )
        parse.epilog = cls.help

        for arg in cls.args:
            flags = arg.pop('flags')
            parse.add_argument(*flags, **arg)

        return vars(parse.parse_args())

if __name__ == "__main__":
    dic = Arg()
    print(dic)
