'''
Author: facsert
Date: 2023-08-08 22:11:46
LastEditTime: 2023-08-29 21:35:11
LastEditors: facsert
Description: 
'''

from textwrap import dedent
from argparse import ArgumentParser, RawDescriptionHelpFormatter


ARGS = [{
        'dest': 'cycle',
        'para': ['-c', '--cycle'],
        'help': 'reboot cycle',
        'action': 'store',
        'default': None,
    },{
        'dest': 'restart_wait',
        'para': ['-t', '--time'],
        'help': 'wait SUT restart time',
        'action': 'store',
        'default': None,
}]

HELP = dedent('''
Before running the script 
Please complete the info in data/config.yaml 

Get script help info
    bash install_model.sh --help

Get script version
    bash install_model.sh --version

run script
    bash install_model.sh 
''')
              
class Arg:

    def __new__(cls):
        return cls.main()
    
    @classmethod
    def prepare(cls):
        cls.args = ARGS
        cls.help = HELP
        cls.params = {}
        cls.parse = None

    @classmethod
    def set_version(cls):
        cls.parse.add_argument(
            '--version', '-v', 
            action='version', 
            version='1.0.0'
        )

    @classmethod
    def create_parser(cls):
        cls.parse = ArgumentParser(
            description='Usage',
            formatter_class=RawDescriptionHelpFormatter,
        )
        for arg in cls.args:
            cls.parse.add_argument(
                *(arg['para']),
                dest = arg.get('dest'),
                action = arg.get('action'), 
                help = arg.get('help'),
                default = arg.get('default'),
            )
        cls.parse.epilog = cls.help
    
    @classmethod
    def parse_args(cls):
        args = cls.parse.parse_args()
        cls.params = vars(args)

    @classmethod
    def main(cls):
        cls.prepare()
        cls.create_parser()
        cls.set_version()
        cls.parse_args()
        return cls.params

if __name__ == "__main__":
    dic = Arg()
    print(dic)