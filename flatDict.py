'''
Author: facsert
Date: 2023-08-03 21:41:52
LastEditTime : 2023-11-08 17:50:49
LastEditors  : Please set LastEditors
Description: 
'''

from json import dumps

class FlatDict(dict): 
    """扁平化字典"""   

    def __init__(self, *args, **kwargs):
        '''
        Description: 初始化属性, flat(扁平化字典) separator(分隔符)
        Return: None
        Attention: 对象存一个原生字典和扁平化字典
        '''        
        super().__init__(*args, **kwargs)
        super().update(*args, **kwargs)
        self.flat = {}
        self.separator = "."
        self.flat_dict(self)

    def update_dict(self, key, value):
        '''
        Description: 解析 key, 将多层 key 逐层解析写入原生字典
        Param key str: 字典 key, 多层 key 包含分隔符 
        Param value Any: 字典 value
        Return: None
        Attention: 
        '''        
        keys, curr = key.split(self.separator), self
        for k in keys[:-1]:
            if isinstance(curr, list):
                curr = curr[int(k)]
                continue

            ret = curr.setdefault(k, {})
            if not isinstance(ret, dict):
                curr.update({k: {}})
            curr = curr[k]
        
        if isinstance(curr, list):
            curr[int(keys[-1])] = value
        else:
            curr[keys[-1]] = value

        self.flat_dict(self)

    def flat_dict(self, data, parent_key=''):
        '''
        Description: 原生字典多层 key 通过分隔符连接写入 flat 字典
        Param dic dict: 原生字典
        Param parent_key dict: 父字典的 key 
        Return: None
        Attention: 任一层的字典 key value 都要保存
        '''        
        if isinstance(data, dict) or isinstance(data, list) or isinstance(data, tuple):
            try:
                group = data.items()
            except AttributeError as e:
                group = enumerate(data)

            for key, value in group:
                new_key = f"{parent_key}{self.separator}{key}" if parent_key else key
                self.flat[new_key] = value
                self.flat_dict(value, new_key)

    def __setitem__(self, key, value):
        '''
        Description: 字典 [] 方式设置值
        Param key str: 原生字典
        Param value Any: 父字典的 key 
        Return: None
        Attention: 
        '''        
        if self.separator in key:
            self.update_dict(key, value)
        else:
            super().__setitem__(key, value)

    def __getitem__(self, key):
        '''
        Description: 字典 [] 获取值
        Param key str: 字典 key, 允许使用多层 key 
        Return Any: 字典 key 对应的 value 
        Attention: 
        '''        
        try:
            return super().__getitem__(key)
        except KeyError:
            return self.flat[key]

    def __delitem__(self, key):
        '''
        Description: 字典删除 key-value
        Param key str: 字典 key, 不允许使用多层 key 
        Return: None
        Attention: 只允许使用原生字典的 key
        '''    
        super().__delitem__(key)
        self.flat = {}
        self.flat_dict(self)

    def __len__(self):
        '''
        Description: 获取原生字典长度
        Return int: 字典长度 
        Attention: 
        '''        
        return super().__len__()

    def update(self, *args, **kwargs):
        '''
        Description: 更新字典
        Return: None 
        Attention: 用法与原生字典一致
        '''        
        super().update(*args, **kwargs)
        self.flat = {}
        self.flat_dict(self)

    def get(self, key, default=None):
        return self.flat.get(key, default)

    def __str__(self):
        '''
        Description: json 格式原生字典
        Return srt: 字典字符串
        Attention: 
        '''
        return dumps(self, indent=4)


if __name__ == '__main__':
    flat = FlatDict({
        'a': {
            'b': { 'c': 1 },
        },
        'e':3,    
    })
    print(flat['a.b'])
    print(flat.get('a.c.d'))
    print(flat)

